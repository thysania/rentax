from services.unit_service import (
    create_unit,
    list_units,
    get_unit,
    update_unit,
    delete_unit,
)


def units_menu():
    while True:
        print("\n=== Units ===")
        print("1. Add unit")
        print("2. List units")
        print("3. Update unit")
        print("4. Delete unit")
        print("0. Back")

        choice = input("Choose an option: ").strip()

        if choice == "1":
            add_unit()
        elif choice == "2":
            show_units()
        elif choice == "3":
            edit_unit()
        elif choice == "4":
            remove_unit()
        elif choice == "0":
            break
        else:
            print("Invalid choice.")


def add_unit():
    reference = input("Reference: ").strip()
    city = input("City (optional): ").strip() or None
    neighborhood = input("Neighborhood (optional): ").strip() or None
    floor = input("Floor (number, optional): ").strip()
    floor = int(floor) if floor.isdigit() else None
    unit_type = input("Unit type (apt/store/building, optional): ").strip() or None

    try:
        create_unit(reference, city, neighborhood, floor, unit_type)
        print("Unit added successfully.")
    except ValueError as e:
        print(f"Error: {e}")


def show_units():
    units = list_units()

    if not units:
        print("No units found.")
        input("\nPress Enter to return...")
        return

    print("\nID | Reference | City | Neighborhood | Floor | Type")
    print("-" * 70)
    for u in units:
        print(
            f"{u['id']} | {u['reference']} | {u['city'] or ''} | {u['neighborhood'] or ''} | {u['floor'] or ''} | {u['unit_type'] or ''}"
        )

    input("\nPress Enter to continue...")


def edit_unit():
    uid = input("Unit ID to update: ").strip()
    if not uid.isdigit():
        print("Invalid ID.")
        return
    uid = int(uid)

    unit = get_unit(uid)
    if not unit:
        print("Unit not found.")
        return

    print("Leave blank to keep current value.")
    reference = input(f"Reference [{unit['reference']}]: ").strip() or None
    city = input(f"City [{unit['city'] or ''}]: ").strip() or None
    neighborhood = input(f"Neighborhood [{unit['neighborhood'] or ''}]: ").strip() or None
    floor = input(f"Floor [{unit['floor'] or ''}]: ").strip()
    floor = int(floor) if floor.isdigit() else None
    unit_type = input(f"Unit type [{unit['unit_type'] or ''}]: ").strip() or None

    try:
        update_unit(uid, reference=reference, city=city, neighborhood=neighborhood, floor=floor, unit_type=unit_type)
        print("Unit updated.")
    except ValueError as e:
        print(f"Error: {e}")


def remove_unit():
    uid = input("Unit ID to delete: ").strip()
    if not uid.isdigit():
        print("Invalid ID.")
        return
    uid = int(uid)

    confirm = input(f"Delete unit {uid}? (y/N): ").strip().lower()
    if confirm != 'y':
        print("Cancelled.")
        return

    try:
        delete_unit(uid)
        print("Unit deleted.")
    except ValueError as e:
        print(f"Error: {e}")