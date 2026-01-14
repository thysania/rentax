from services.client_service import (
    create_client,
    list_clients,
    get_client,
    update_client,
    delete_client,
)


def clients_menu():
    while True:
        print("\n=== Clients ===")
        print("1. Add client")
        print("2. List clients")
        print("3. Update client")
        print("4. Delete client")
        print("0. Back")

        choice = input("Choose an option: ").strip()

        if choice == "1":
            add_client()
        elif choice == "2":
            show_clients()
        elif choice == "3":
            edit_client()
        elif choice == "4":
            remove_client()
        elif choice == "0":
            break
        else:
            print("Invalid choice.")


def add_client():
    name = input("Name: ").strip()
    phone = input("Phone (optional): ").strip() or None
    legal_id = input("Legal ID (optional): ").strip() or None
    client_type = input("Client type (PP/PM): ").strip().upper()

    try:
        create_client(name, client_type, phone, legal_id)
        print("Client added successfully.")
    except ValueError as e:
        print(f"Error: {e}")


def show_clients():
    clients = list_clients()

    if not clients:
        print("No clients found.")
        input("\nPress Enter to return...")
        return

    print("\nID | Name | Type | Phone | Legal ID")
    print("-" * 60)
    for c in clients:
        print(
            f"{c['id']} | {c['name']} | {c['client_type']} | {c['phone'] or ''} | "
            f"{c['legal_id'] or ''}"
        )

    input("\nPress Enter to continue...")


def edit_client():
    cid = input("Client ID to update: ").strip()
    if not cid.isdigit():
        print("Invalid ID.")
        return
    cid = int(cid)

    client = get_client(cid)
    if not client:
        print("Client not found.")
        return

    print("Leave blank to keep current value.")
    name = input(f"Name [{client['name']}]: ").strip() or None
    phone = input(f"Phone [{client['phone'] or ''}]: ").strip() or None
    legal_id = input(f"Legal ID [{client['legal_id'] or ''}]: ").strip() or None
    client_type = input(f"Client type [{client['client_type']}]: ").strip().upper() or None

    try:
        update_client(cid, name=name, client_type=client_type, phone=phone, legal_id=legal_id)
        print("Client updated.")
    except ValueError as e:
        print(f"Error: {e}")


def remove_client():
    cid = input("Client ID to delete: ").strip()
    if not cid.isdigit():
        print("Invalid ID.")
        return
    cid = int(cid)

    confirm = input(f"Delete client {cid}? (y/N): ").strip().lower()
    if confirm != 'y':
        print("Cancelled.")
        return

    try:
        delete_client(cid)
        print("Client deleted.")
    except ValueError as e:
        print(f"Error: {e}")