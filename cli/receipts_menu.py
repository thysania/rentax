from services.receipt_service import list_receipt_logs_with_names, create_receipt
from services.taxes_service import write_csv_file


def receipts_menu():
    while True:
        print("\n=== Receipts ===")
        print("1. Generate receipts for a month (batch)")
        print("2. Show receipt logs")
        print("3. Record payment for receipt log UID")
        print("4. Export receipts/payments CSV")
        print("0. Back")

        choice = input("Choose an option: ").strip()

        if choice == "1":
            from services.receipt_service import batch_generate_receipts_for_month
            month = input("Enter month to generate receipts for (mm/yyyy): ").strip()
            issue_date = input("Issue date for all receipts (dd/mm/yyyy): ").strip()
            try:
                count = batch_generate_receipts_for_month(month, issue_date)
                print(f"Generated {count} receipts for {month}.")
            except Exception as e:
                print(f"Error: {e}")
        elif choice == "2":
            show_receipt_logs()
        elif choice == "3":
            record_payment()
        elif choice == "4":
            export_receipts_csv()
        elif choice == "0":
            break
        else:
            print("Invalid choice.")


def show_receipt_logs():
    rows = list_receipt_logs_with_names()

    if not rows:
        print("\nNo receipt logs found.")
        input("\nPress Enter to return...")
        return

    print("\nUID | Unit | Owner | Client | No | Period | Issue | Amount")
    print("-" * 110)
    for r in rows:
        print(
            f"{r['uid']} | {r['unit_reference']} | {r['owner_name']} | {r['client_name']} | {r['receipt_no']} | {r['period']} | {r['issue_date']} | {r['amount']}"
        )

    input("\nPress Enter to continue...")


def record_payment():
    from services.payments_service import create_payment

    uid = input("Receipt log UID: ").strip()
    amount = input("Amount received: ").strip()
    received_at = input("Received date (dd/mm/yyyy) [today]: ").strip()
    note = input("Note (optional): ").strip()

    if not uid.isdigit():
        print("UID must be numeric.")
        return
    try:
        amount_val = float(amount)
    except Exception:
        print("Invalid amount.")
        return

    received_at_val = received_at if received_at else None

    try:
        create_payment(int(uid), amount_val, received_at_val, note if note else None)
        print("Payment recorded.")
    except Exception as e:
        print(f"Error recording payment: {e}")


def export_receipts_csv():
    year = input("Year (YYYY): ").strip()
    owner = input("Owner ID (blank = all owners): ").strip()
    if not year.isdigit():
        print("Invalid year format.")
        return
    year = int(year)
    print("Select format:")
    print("1. detailed (lines per receipt)")
    print("2. by-owner (owner aggregation)")
    print("3. minimal")
    fmt_choice = input("Choose format [1]: ").strip() or '1'
    fmt_map = {'1': 'detailed', '2': 'by-owner', '3': 'minimal'}
    fmt = fmt_map.get(fmt_choice, 'detailed')
    out = input(f"Output file (path) or '-' for stdout [receipts_{year}.csv]: ").strip() or f"receipts_{year}.csv"

    from services.receipt_service import generate_receipts_report

    try:
        headers, rows = generate_receipts_report(year, csv_format=fmt, owner_id=(int(owner) if owner else None))
    except ValueError as e:
        print(f"Error: {e}")
        return

    out_content = write_csv_file(out, headers, rows)
    if out == '-':
        print(out_content)
    else:
        print(f"Wrote CSV to {out}")