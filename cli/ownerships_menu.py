from services.ownership_service import (
    create_ownership,
    list_ownerships,
    list_ownerships_with_names,
    get_ownership,
    update_ownership,
    delete_ownership,
)


def ownerships_menu():
    while True:
        print("\n=== Ownerships ===")
        print("1. Add ownership")
        print("2. List ownerships")
        print("3. Update ownership")
        print("4. Delete ownership")
        print("0. Back")

        choice = input("Choose an option: ").strip()

        if choice == "1":
            add_ownership()
        elif choice == "2":
            show_ownerships()
        elif choice == "3":
            edit_ownership()
        elif choice == "4":
            remove_ownership()
        elif choice == "0":
            break
        else:
            print("Invalid choice.")


def add_ownership():
    unit_id = input("Unit ID: ").strip()
    owner_id = input("Owner ID: ").strip()
    share = input("Share percent (e.g. 50): ").strip()
    alternate = input("Alternate? (y/N): ").strip().lower()

    if not unit_id.isdigit() or not owner_id.isdigit():
        print("Unit ID and Owner ID must be numeric.")
        return

    try:
        share_val = float(share)
    except ValueError:
        print("share_percent must be a number.")
        return

    alt_val = 1 if alternate == 'y' else 0
    odd_even = None
    if alt_val == 1:
        odd_even = input("odd or even? (odd/even): ").strip().lower()
        if odd_even not in ("odd", "even"):
            print("odd_even must be 'odd' or 'even'")
            return

    try:
        create_ownership(int(unit_id), int(owner_id), share_val, alt_val, odd_even)
        print("Ownership added successfully.")
    except ValueError as e:
        print(f"Error: {e}")


def show_ownerships():
    uid = input("Unit ID to filter by (blank = all): ").strip()
    rows = list_ownerships_with_names(int(uid)) if uid.isdigit() else list_ownerships_with_names()

    if not rows:
        print("No ownerships found.")
        return

    print("\nID | Unit Ref | Owner | Share% | Alternate | Odd/Even")
    print("-" * 80)
    for r in rows:
        print(
            f"{r['id']} | {r['unit_reference']} | {r['owner_name']} | {r['share_percent']} | {r['alternate']} | {r['odd_even'] or ''}"
        )

    input("\nPress Enter to continue...")


def edit_ownership():
    oid = input("Ownership ID to update: ").strip()
    if not oid.isdigit():
        print("Invalid ID.")
        return
    oid = int(oid)

    row = get_ownership(oid)
    if not row:
        print("Ownership not found.")
        return

    print("Leave blank to keep current value.")
    share = input(f"Share percent [{row['share_percent']}]: ").strip() or None
    alternate = input(f"Alternate (y/N) [{ 'y' if row['alternate'] == 1 else 'N' }]: ").strip().lower() or None
    odd_even = None
    if alternate is not None:
        alt_val = 1 if alternate == 'y' else 0
        if alt_val == 1:
            odd_even = input(f"odd or even [{row['odd_even'] or ''}]: ").strip().lower() or None
            if odd_even is not None and odd_even not in ("odd", "even"):
                print("odd_even must be 'odd' or 'even'")
                return
    else:
        alt_val = None

    share_val = None
    if share is not None:
        try:
            share_val = float(share)
        except ValueError:
            print("share_percent must be a number.")
            return

    try:
        update_ownership(oid, share_percent=share_val, alternate=alt_val, odd_even=odd_even)
        print("Ownership updated.")
    except ValueError as e:
        print(f"Error: {e}")


def remove_ownership():
    oid = input("Ownership ID to delete: ").strip()
    if not oid.isdigit():
        print("Invalid ID.")
        return
    oid = int(oid)

    confirm = input(f"Delete ownership {oid}? (y/N): ").strip().lower()
    if confirm != 'y':
        print("Cancelled.")
        return

    try:
        delete_ownership(oid)
        print("Ownership deleted.")
    except ValueError as e:
        print(f"Error: {e}")