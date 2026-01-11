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

    return {
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