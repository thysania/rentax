from services.assignment_service import (
    create_assignment,
    list_assignments,
    list_assignments_with_names,
    get_assignment,
    update_assignment,
    delete_assignment,
)


def assignments_menu():
    while True:
        print("\n=== Assignments ===")
        print("1. Add assignment")
        print("2. List assignments")
        print("3. Update assignment")
        print("4. Delete assignment")
        print("0. Back")

        choice = input("Choose an option: ").strip()

        if choice == "1":
            add_assignment()
        elif choice == "2":
            show_assignments()
        elif choice == "3":
            edit_assignment()
        elif choice == "4":
            remove_assignment()
        elif choice == "0":
            break
        else:
            print("Invalid choice.")


def add_assignment():
    unit_id = input("Unit ID: ").strip()
    client_id = input("Client ID: ").strip()
    start_date = input("Start date (dd/mm/yyyy): ").strip()
    end_date = input("End date (dd/mm/yyyy, optional): ").strip() or None
    rent_amount = input("Rent amount: ").strip()
    ras_ir = input("ras_ir (0 or 1, default 0): ").strip()

    if not unit_id.isdigit() or not client_id.isdigit():
        print("Unit ID and Client ID must be numeric.")
        return
    unit_id = int(unit_id)
    client_id = int(client_id)

    if not rent_amount:
        print("rent_amount is required.")
        return

    try:
        rent_amount_val = float(rent_amount)
    except ValueError:
        print("rent_amount must be a number.")
        return

    ras_ir = int(ras_ir) if ras_ir in ("0", "1") else 0

    try:
        create_assignment(unit_id, client_id, start_date, end_date, rent_amount_val, ras_ir)
        print("Assignment added successfully.")
    except ValueError as e:
        print(f"Error: {e}")


def show_assignments():
    rows = list_assignments_with_names()

    if not rows:
        print("No assignments found.")
        input("\nPress Enter to return...")
        return

    print("\nID | Unit Ref | Client | Start | End | Rent | ras_ir")
    print("-" * 100)
    for r in rows:
        print(
            f"{r['id']} | {r['unit_reference']} | {r['client_name']} | {r['start_date']} | {r['end_date'] or ''} | {r['rent_amount']} | {r['ras_ir']}"
        )

    input("\nPress Enter to continue...")


def edit_assignment():
    aid = input("Assignment ID to update: ").strip()
    if not aid.isdigit():
        print("Invalid ID.")
        return
    aid = int(aid)

    row = get_assignment(aid)
    if not row:
        print("Assignment not found.")
        return

    print("Leave blank to keep current value.")
    start_date = input(f"Start date [{row['start_date']} dd/mm/yyyy]: ").strip() or None
    end_date = input(f"End date [{row['end_date'] or ''} dd/mm/yyyy]: ").strip() or None
    rent = input(f"Rent amount [{row['rent_amount']}]: ").strip() or None
    ras_ir = input(f"ras_ir [{row['ras_ir']}]: ").strip()
    ras_ir_val = int(ras_ir) if ras_ir in ("0", "1") else None

    rent_val = None
    if rent is not None:
        try:
            rent_val = float(rent)
        except ValueError:
            print("rent_amount must be a number.")
            return

    try:
        update_assignment(aid, start_date=start_date, end_date=end_date, rent_amount=rent_val, ras_ir=ras_ir_val)
        print("Assignment updated.")
    except ValueError as e:
        print(f"Error: {e}")


def remove_assignment():
    aid = input("Assignment ID to delete: ").strip()
    if not aid.isdigit():
        print("Invalid ID.")
        return
    aid = int(aid)

    confirm = input(f"Delete assignment {aid}? (y/N): ").strip().lower()
    if confirm != 'y':
        print("Cancelled.")
        return

    try:
        delete_assignment(aid)
        print("Assignment deleted.")
    except ValueError as e:
        print(f"Error: {e}")