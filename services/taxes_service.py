from database import get_connection
from config import TAX_CONFIG
from services.payments_service import sum_received_for_owner_year


def _find_ir_bracket(taxable):
    for mn, mx, rate, deduction in TAX_CONFIG['ir_brackets']:
        if mx is None:
            if taxable >= mn:
                return rate, deduction, (mn, mx)
        else:
            if mn <= taxable <= mx:
                return rate, deduction, (mn, mx)
    # fallback
    return 0.0, 0, (0, 0)


def _find_ras_rate(gross):
    for mn, mx, rate in TAX_CONFIG['ras_thresholds']:
        if mx is None:
            if gross >= mn:
                return rate, (mn, mx)
        else:
            if mn <= gross <= mx:
                return rate, (mn, mx)
    return 0.0, (0, 0)


def compute_owner_taxes_for_year(owner_id, year):
    conn = get_connection()
    cur = conn.cursor()

    # 1) gross revenue: sum of receipt_log.amount for that owner where period matches year
    cur.execute(
        "SELECT COALESCE(SUM(amount), 0.0) FROM receipt_log WHERE owner_id = ? AND substr(period,1,4) = ?",
        (owner_id, str(year)),
    )
    gross = float(cur.fetchone()[0] or 0.0)

    # 2) taxable = gross * (1 - abattement)
    abattement = TAX_CONFIG.get('abattement', 0.40)
    taxable = gross * (1.0 - abattement)

    # 3) apply IR bracket
    rate, deduction, bracket = _find_ir_bracket(taxable)
    # initial tax is computed without final rounding (rounding only at the very end)
    initial_tax = taxable * rate - deduction

    # 4) family deduction
    cur.execute("SELECT family_count FROM owners WHERE id = ?", (owner_id,))
    row = cur.fetchone()
    family_count = int(row[0]) if row else 0
    per_person = TAX_CONFIG.get('family_deduction_per_person', 500)
    fam_max = TAX_CONFIG.get('family_deduction_max', 3000)
    fam_deduction = min(per_person * family_count, fam_max)

    tax_after_family = initial_tax - fam_deduction

    # 5) deduct RAS that client took: compute actual withheld = gross - sum(received)
    received = sum_received_for_owner_year(owner_id, year)
    ras_withheld = gross - received

    # Also compute theoretical ras rate for reference
    ras_rate, ras_bracket = _find_ras_rate(gross)
    theoretical_ras = round(gross * ras_rate, 2)

    tax_after_ras = tax_after_family - ras_withheld

    # Final tax: round up to the nearest whole number and ensure non-negative
    import math

    final_tax = max(0, math.ceil(tax_after_ras))

    res = {
        'owner_id': owner_id,
        'year': year,
        'gross_revenue': round(gross, 2),
        'taxable_amount': round(taxable, 2),
        'ir_rate': rate,
        'ir_deduction': deduction,
        'initial_tax': initial_tax,
        'family_count': family_count,
        'family_deduction': fam_deduction,
        'tax_after_family': tax_after_family,
        'ras_rate': ras_rate,
        'theoretical_ras': theoretical_ras,
        'ras_withheld': ras_withheld,
        'final_tax': final_tax,
        'bracket': bracket,
        'ras_bracket': ras_bracket,
    }

    return res


# Report generation utilities
import csv
import io


def _assignment_summaries_for_owner(owner_id, year):
    """Return list of per-assignment rows for owner-year.
    Each item: dict with assignment_id, unit_ref, unit_city, client_name, client_legal_id, gross
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT rl.uid, rl.assignment_id, u.reference, u.city, c.name, c.legal_id, rl.amount
        FROM receipt_log rl
        JOIN assignments a ON a.id = rl.assignment_id
        JOIN units u ON u.id = a.unit_id
        JOIN clients c ON c.id = rl.client_id
        WHERE rl.owner_id = ? AND substr(rl.period,1,4) = ?
        ORDER BY rl.uid
        """,
        (owner_id, str(year)),
    )
    rows = []
    for uid, assignment_id, ref, city, client_name, client_legal_id, amount in cur.fetchall():
        rows.append(
            {
                'receipt_uid': uid,
                'assignment_id': assignment_id,
                'unit_reference': ref,
                'unit_city': city,
                'client_name': client_name,
                'client_legal_id': client_legal_id,
                'gross': float(amount or 0.0),
            }
        )
    conn.close()
    return rows


def generate_taxes_report(year, csv_format='detailed', owner_id=None):
    """Generate taxes report data for the given year.

    csv_format: 'detailed' (one line per owner with fields),
                'by-assignment' (lines per assignment then owner summary),
                'minimal' (owner, year, gross, rounded_tax)
    If owner_id is provided, limit report to that owner.

    Returns: (headers, rows) where rows is list of dicts.
    """
    # collect owners list
    conn = get_connection()
    cur = conn.cursor()
    if owner_id is not None:
        cur.execute("SELECT id, name, legal_id FROM owners WHERE id = ?", (owner_id,))
    else:
        cur.execute("SELECT id, name, legal_id FROM owners ORDER BY id")
    owners = cur.fetchall()

    report_rows = []

    for oid, name, legal_id in owners:
        # compute aggregate
        agg = compute_owner_taxes_for_year(oid, year)

        if csv_format == 'minimal':
            headers = ['owner_id', 'owner_name', 'year', 'gross_revenue', 'rounded_tax']
            report_rows.append(
                {
                    'owner_id': oid,
                    'owner_name': name,
                    'year': year,
                    'gross_revenue': f"{agg['gross_revenue']:.2f}",
                    'rounded_tax': f"{agg['final_tax']}",
                }
            )
            continue

        if csv_format == 'by-assignment':
            # produce assignment lines first
            assignment_headers = [
                'owner_id',
                'owner_name',
                'owner_legal_id',
                'unit_reference',
                'unit_city',
                'client_name',
                'client_legal_id',
                'assignment_id',
                'gross',
            ]
            summary_headers = [
                'gross_revenue',
                'abattement_amount',
                'tax_after_rate_minus_deduction',
                'family_deduction',
                'final_tax_unrounded',
                'rounded_tax',
                'ras_withheld',
                'due_tax',
            ]
            # combined headers (assignment columns first, then summary columns)
            headers = assignment_headers + summary_headers

            ass_rows = _assignment_summaries_for_owner(oid, year)
            for a in ass_rows:
                report_rows.append(
                    {
                        'owner_id': oid,
                        'owner_name': name,
                        'owner_legal_id': legal_id,
                        'unit_reference': a['unit_reference'] or '',
                        'unit_city': a['unit_city'] or '',
                        'client_name': a['client_name'] or '',
                        'client_legal_id': a['client_legal_id'] or '',
                        'assignment_id': a['assignment_id'],
                        'gross': f"{a['gross']:.2f}",
                    }
                )
            # add an empty separator row, then owner summary below
            report_rows.append({})
            # fallthrough to add owner summary

        # detailed (owner summary)
        if csv_format == 'detailed':
            headers = [
                'owner_id',
                'owner_name',
                'owner_legal_id',
                'gross_revenue',
                'abattement_amount',
                'tax_after_rate_minus_deduction',
                'family_deduction',
                'final_tax_unrounded',
                'rounded_tax',
                'ras_withheld',
                'due_tax',
            ]
        else:
            # for by-assignment we already set headers above (combined headers)
            pass

        # compute abattement amount from taxable (we show amount = gross * abattement)
        abattement_pct = 1.0 - (agg['taxable_amount'] / (agg['gross_revenue'] or 1)) if agg['gross_revenue'] else 0.0
        abattement_amount = round(agg['gross_revenue'] * abattement_pct, 2)

        tax_after_rate_minus_deduction = agg['initial_tax']
        final_unrounded = agg['tax_after_family'] - (agg['ras_withheld'] or 0.0)
        rounded_tax = agg['final_tax']
        due_tax = rounded_tax - agg['ras_withheld']

        report_rows.append(
            {
                'owner_id': oid,
                'owner_name': name,
                'owner_legal_id': legal_id or '',
                'gross_revenue': f"{agg['gross_revenue']:.2f}",
                'abattement_amount': f"{abattement_amount:.2f}",
                'tax_after_rate_minus_deduction': f"{tax_after_rate_minus_deduction:.2f}",
                'family_deduction': f"{agg['family_deduction']:.2f}",
                'final_tax_unrounded': f"{final_unrounded:.2f}",
                'rounded_tax': f"{rounded_tax}",
                'ras_withheld': f"{agg['ras_withheld']:.2f}",
                'due_tax': f"{due_tax:.2f}",
            }
        )

    conn.close()

    return headers, report_rows


def write_csv_file(path, headers, rows):
    mode = 'w'
    if path == '-':
        # return string
        sio = io.StringIO()
        writer = csv.DictWriter(sio, fieldnames=headers)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)
        return sio.getvalue()

    with open(path, mode, newline='', encoding='utf-8') as fh:
        writer = csv.DictWriter(fh, fieldnames=headers)
        writer.writeheader()
        for r in rows:
            # ensure all headers present
            row = {k: r.get(k, '') for k in headers}
            writer.writerow(row)
    return None