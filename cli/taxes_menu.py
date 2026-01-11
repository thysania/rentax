from services.taxes_service import compute_owner_taxes_for_year, generate_taxes_report, write_csv_file


def taxes_menu():
    print("\n=== Taxes ===")
    year = input("Year (YYYY): ").strip()
    owner = input("Owner ID (blank = all owners): ").strip()

    if not year.isdigit():
        print("Invalid year format.")
        return
    year = int(year)

    if owner:
        if not owner.isdigit():
            print("Invalid owner ID.")
            return
        owner_id = int(owner)
        res = compute_owner_taxes_for_year(owner_id, year)
        _print_tax_result(res)
    else:
        # list taxes for all owners
        from database import get_connection
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT id FROM owners ORDER BY id")
        owners = [r[0] for r in cur.fetchall()]
        conn.close()
        for oid in owners:
            res = compute_owner_taxes_for_year(oid, year)
            _print_tax_result(res)

    # Offer CSV export
    exp = input("Export CSV report? (y/N): ").strip().lower()
    if exp == 'y':
        fmt = input("Format - 'detailed' (one owner line), 'by-assignment' (lines per assignment then owner summary), 'minimal' : ").strip() or 'detailed'
        out = input("Output file (path) or '-' for stdout [taxes_{}.csv]: ".format(year)).strip() or f"taxes_{year}.csv"
        headers, rows = generate_taxes_report(year, csv_format=fmt, owner_id=(int(owner) if owner else None))
        out_content = write_csv_file(out, headers, rows)
        if out == '-':
            print(out_content)
        else:
            print(f"Wrote CSV to {out}")


def _print_tax_result(res):
    print(f"\nOwner {res['owner_id']} - Year {res['year']}")
    print(f"Gross revenue: {res['gross_revenue']}")
    print(f"Taxable (after abattement): {res['taxable_amount']}")
    print(f"Initial tax (rate {res['ir_rate']}, deduction {res['ir_deduction']}): {res['initial_tax']}")
    print(f"Family deduction ({res['family_count']}): {res['family_deduction']}")
    print(f"Tax after family deduction: {res['tax_after_family']}")
    print(f"RAS withheld: {res['ras_withheld']} (theoretical {res['theoretical_ras']} at rate {res['ras_rate']})")
    print(f"Final tax: {res['final_tax']}")
