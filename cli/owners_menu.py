from services.owner_service import create_owner, list_owners


def owners_menu():
    while True:
        print("\n=== Owners ===")
        print("1. Add owner")
        print("2. List owners")
        print("0. Back")

        choice = input("Choose an option: ").strip()

        if choice == "1":
            add_owner()
        elif choice == "2":
            show_owners()
        elif choice == "0":
            break
        else:
            print("Invalid choice.")


def add_owner():
    name = input("Name: ").strip()
    phone = input("Phone (optional): ").strip() or None
    legal_id = input("Legal ID (CIN / IF): ").strip() or None
    family_count = input("Family count (number): ").strip()

    family_count = int(family_count) if family_count.isdigit() else 0

    create_owner(name, phone, legal_id, family_count)
    print("Owner added successfully.")


def show_owners():
    owners = list_owners()

    if not owners:
        print("No owners found.")
        return

    print("\nID | Name | Phone | Legal ID | Family Count")
    print("-" * 45)
    for o in owners:
        print(
            f"{o['id']} | {o['name']} | {o['phone'] or ''} | "
            f"{o['legal_id'] or ''} | {o['family_count']}"
        )

    input("\nPress Enter to continue...")