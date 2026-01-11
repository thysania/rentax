from services.receipt_service import list_receipt_logs_with_names, create_receipt


def receipts_menu():
    while True:
        print("\n=== Receipts ===")
        print("1. Create receipt (split and log)")
        print("2. Show receipt logs")
        print("3. Record payment for receipt log UID")
        print("0. Back")

        choice = input("Choose an option: ").strip()

        if choice == "1":
            add_receipt()
        elif choice == "2":
            show_receipt_logs()
        elif choice == "3":
            record_payment()
        elif choice == "0":
            break
        else:
            print("Invalid choice.")


def add_receipt():
    aid = input("Assignment ID: ").strip()
    period = input("Period (YYYY-MM-DD): ").strip()
    issue_date = input("Issue date (YYYY-MM-DD): ").strip()
    amount = input("Total amount: ").strip()

    if not aid.isdigit():
        print("Assignment ID must be numeric.")
        return
    aid = int(aid)

    try:
        amount_val = float(amount)
    except Exception:
        print("Invalid amount.")
        return

    try:
        create_receipt(aid, period, issue_date, amount_val)
        print("Receipt created and split to owners.")
    except ValueError as e:
        print(f"Error: {e}")


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
    received_at = input("Received date (YYYY-MM-DD) [today]: ").strip()
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