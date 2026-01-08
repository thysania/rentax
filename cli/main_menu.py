from cli.owners_menu import owners_menu
from cli.clients_menu import clients_menu
from cli.units_menu import units_menu
from cli.assignments_menu import assignments_menu
from cli.receipts_menu import receipts_menu
from cli.taxes_menu import taxes_menu


def main_menu():
    while True:
        print("\n=== RENT MANAGER ===")
        print("1. Owners")
        print("2. Clients")
        print("3. Units")
        print("4. Assignments")
        print("5. Receipts")
        print("6. Taxes")
        print("0. Exit")

        choice = input("Choose an option: ").strip()

        if choice == "1":
            owners_menu()
        elif choice == "2":
            clients_menu()
        elif choice == "3":
            units_menu()
        elif choice == "4":
            assignments_menu()
        elif choice == "5":
            receipts_menu()
        elif choice == "6":
            taxes_menu()
        elif choice == "0":
            print("Goodbye.")
            break
        else:
            print("Invalid choice.")