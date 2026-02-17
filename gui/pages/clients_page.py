import flet as ft
from flet import icons
from gui.components.common import create_header, create_text_field, create_form_field_row
from services import client_service


def create(page: ft.Page):
    """Create clients management page"""
    
    # Dialog and snackbar
    dlg = ft.AlertDialog()
    page.dialog = dlg
    
    snackbar = ft.SnackBar(ft.Text(""))
    page.overlay.append(snackbar)
    
    # Form fields
    name_field = create_text_field("Client Name", "e.g., John Doe")
    phone_field = create_text_field("Phone", "Optional")
    legal_id_field = create_text_field("Legal ID", "e.g., Tax ID")
    
    # Client type dropdown
    client_type_dropdown = ft.Dropdown(
        label="Client Type",
        value="PP",
        options=[
            ft.dropdown.Option("PP", text="Person (PP)"),
            ft.dropdown.Option("PM", text="Company (PM)"),
        ],
        border_radius=6,
    )
    
    # Data table
    clients_table = ft.Column(controls=[], spacing=8)
    
    def load_clients():
        """Load clients into table"""
        try:
            clients = client_service.list_all_clients() or []
            
            rows = []
            for client in clients:
                rows.append(
                    ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text(str(client.get('id', '')))),
                            ft.DataCell(ft.Text(client.get('name', ''))),
                            ft.DataCell(ft.Text(client.get('phone', 'N/A'))),
                            ft.DataCell(ft.Text(client.get('legal_id', 'N/A'))),
                            ft.DataCell(ft.Text(client.get('client_type', 'N/A'))),
                            ft.DataCell(
                                ft.Row(
                                    controls=[
                                        ft.IconButton(
                                            icon=icons.EDIT,
                                            icon_size=18,
                                            on_click=lambda e, c=client: edit_client(c),
                                        ),
                                        ft.IconButton(
                                            icon=icons.DELETE,
                                            icon_size=18,
                                            on_click=lambda e, c=client: delete_client(c),
                                        ),
                                    ],
                                    spacing=4,
                                )
                            ),
                        ]
                    )
                )
            
            clients_table.controls = [
                ft.DataTable(
                    columns=[
                        ft.DataColumn(ft.Text("ID", weight="w500")),
                        ft.DataColumn(ft.Text("Name", weight="w500")),
                        ft.DataColumn(ft.Text("Phone", weight="w500")),
                        ft.DataColumn(ft.Text("Legal ID", weight="w500")),
                        ft.DataColumn(ft.Text("Type", weight="w500")),
                        ft.DataColumn(ft.Text("Actions", weight="w500")),
                    ],
                    rows=rows,
                    border=ft.border.all(1, "#E0E0E0"),
                    border_radius=8,
                )
            ]
            page.update()
        except Exception as e:
            show_error(f"Error loading clients: {str(e)}")
    
    def show_error(message: str):
        """Show error message"""
        snackbar.content = ft.Text(message, color="white")
        snackbar.bgcolor = "#F44336"
        snackbar.open = True
        page.update()
    
    def show_success(message: str):
        """Show success message"""
        snackbar.content = ft.Text(message, color="white")
        snackbar.bgcolor = "#4CAF50"
        snackbar.open = True
        page.update()
    
    def clear_form():
        """Clear form fields"""
        name_field.value = ""
        phone_field.value = ""
        legal_id_field.value = ""
        client_type_dropdown.value = "PP"
    
    def add_client(e):
        """Add new client"""
        if not name_field.value:
            show_error("Name is required")
            return
        
        if not client_type_dropdown.value:
            show_error("Client type is required")
            return
        
        try:
            client_service.create_client(
                name=name_field.value,
                phone=phone_field.value or None,
                legal_id=legal_id_field.value or None,
                client_type=client_type_dropdown.value,
            )
            show_success("Client added successfully")
            clear_form()
            load_clients()
            form_container.visible = False
            page.update()
        except Exception as ex:
            show_error(f"Error: {str(ex)}")
    
    def edit_client(client):
        """Edit client"""
        name_field.value = client.get('name', '')
        phone_field.value = client.get('phone', '')
        legal_id_field.value = client.get('legal_id', '')
        client_type_dropdown.value = client.get('client_type', 'PP')
        form_container.visible = True
        page.update()
    
    def delete_client(client):
        """Delete client"""
        def confirm():
            try:
                client_service.delete_client(client['id'])
                show_success("Client deleted successfully")
                load_clients()
                dlg.open = False
                page.update()
            except Exception as ex:
                show_error(f"Error: {str(ex)}")
        
        dlg.title = ft.Text("Confirm Delete")
        dlg.content = ft.Text(f"Delete '{client.get('name', '')}'?")
        dlg.actions = [
            ft.TextButton("Cancel", on_click=lambda e: close_dialog(e)),
            ft.ElevatedButton("Delete", on_click=lambda e: confirm()),
        ]
        dlg.open = True
        page.update()
    
    def close_dialog(e):
        """Close dialog"""
        dlg.open = False
        page.update()
    
    # Form container
    form_container = ft.Container(
        content=ft.Column(
            controls=[
                ft.Text("Add New Client", size=16, weight="bold"),
                create_form_field_row("Name", name_field),
                create_form_field_row("Phone", phone_field),
                create_form_field_row("Legal ID", legal_id_field),
                ft.Row(
                    controls=[
                        ft.Container(
                            content=ft.Text("Client Type", size=13, weight="w500", color="#333"),
                            width=150,
                        ),
                        ft.Container(expand=True, content=client_type_dropdown),
                    ],
                    spacing=12,
                    vertical_alignment=ft.CrossAxisAlignment.START,
                    height=60,
                ),
                ft.Row(
                    controls=[
                        ft.ElevatedButton(
                            "Save",
                            icon=icons.SAVE,
                            on_click=add_client,
                        ),
                        ft.TextButton(
                            "Cancel",
                            on_click=lambda e: setattr(form_container, 'visible', False) or page.update(),
                        ),
                    ],
                    spacing=12,
                ),
            ],
            spacing=12,
        ),
        padding=16,
        bgcolor="white",
        border_radius=8,
        border=ft.border.all(1, "#E0E0E0"),
        visible=False,
        margin=ft.margin.only(bottom=20),
    )
    
    # Main content
    load_clients()
    
    content = ft.Column(
        controls=[
            create_header("Clients", "Manage tenants and businesses"),
            ft.ElevatedButton(
                "Add Client",
                icon=icons.ADD,
                on_click=lambda e: setattr(form_container, 'visible', not form_container.visible) or page.update(),
            ),
            form_container,
            ft.Container(
                content=ft.Text("Clients List", size=16, weight="bold"),
                margin=ft.margin.only(top=20),
            ),
            clients_table,
        ],
        spacing=16,
        scroll=ft.ScrollMode.AUTO,
    )
    
    return content
