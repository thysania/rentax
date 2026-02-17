import flet as ft
from flet import icons
from gui.components.common import (
    create_header, create_button, create_text_field, 
    create_form_field_row, create_snackbar
)
from services import owner_service


def create(page: ft.Page):
    """Create owners management page"""
    
    # Dialog and snackbar
    dlg = ft.AlertDialog()
    page.dialog = dlg
    
    snackbar = ft.SnackBar(ft.Text(""))
    page.overlay.append(snackbar)
    
    # Form fields
    name_field = create_text_field("Owner Name", "e.g., John Doe")
    phone_field = create_text_field("Phone", "Optional")
    legal_id_field = create_text_field("Legal ID", "e.g., Tax ID")
    family_count_field = create_text_field("Family Count", "Number of family members")
    
    # Data table
    owners_table = ft.Column(
        controls=[],
        spacing=8,
    )
    
    def load_owners():
        """Load owners into table"""
        try:
            owners = owner_service.list_owners() or []
            
            rows = []
            for owner in owners:
                rows.append(
                    ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text(str(owner.get('id', '')))),
                            ft.DataCell(ft.Text(owner.get('name', ''))),
                            ft.DataCell(ft.Text(owner.get('phone', 'N/A'))),
                            ft.DataCell(ft.Text(owner.get('legal_id', 'N/A'))),
                            ft.DataCell(ft.Text(str(owner.get('family_count', 0)))),
                            ft.DataCell(
                                ft.Row(
                                    controls=[
                                        ft.IconButton(
                                            icon=icons.EDIT,
                                            icon_size=18,
                                            on_click=lambda e, o=owner: edit_owner(o),
                                        ),
                                        ft.IconButton(
                                            icon=icons.DELETE,
                                            icon_size=18,
                                            on_click=lambda e, o=owner: delete_owner(o),
                                        ),
                                    ],
                                    spacing=4,
                                )
                            ),
                        ]
                    )
                )
            
            owners_table.controls = [
                ft.DataTable(
                    columns=[
                        ft.DataColumn(ft.Text("ID", weight="w500")),
                        ft.DataColumn(ft.Text("Name", weight="w500")),
                        ft.DataColumn(ft.Text("Phone", weight="w500")),
                        ft.DataColumn(ft.Text("Legal ID", weight="w500")),
                        ft.DataColumn(ft.Text("Family Count", weight="w500")),
                        ft.DataColumn(ft.Text("Actions", weight="w500")),
                    ],
                    rows=rows,
                    border=ft.border.all(1, "#E0E0E0"),
                    border_radius=8,
                )
            ]
            page.update()
        except Exception as e:
            show_error(f"Error loading owners: {str(e)}")
    
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
        family_count_field.value = ""
    
    def add_owner(e):
        """Add new owner"""
        if not name_field.value:
            show_error("Name is required")
            return
        
        try:
            owner_service.create_owner(
                name=name_field.value,
                phone=phone_field.value or None,
                legal_id=legal_id_field.value or None,
                family_count=int(family_count_field.value or 0),
            )
            show_success("Owner added successfully")
            clear_form()
            load_owners()
            form_container.visible = False
            page.update()
        except Exception as ex:
            show_error(f"Error: {str(ex)}")
    
    def edit_owner(owner):
        """Edit owner"""
        name_field.value = owner.get('name', '')
        phone_field.value = owner.get('phone', '')
        legal_id_field.value = owner.get('legal_id', '')
        family_count_field.value = str(owner.get('family_count', 0))
        form_container.visible = True
        page.update()
    
    def delete_owner(owner):
        """Delete owner"""
        def confirm():
            try:
                owner_service.delete_owner(owner['id'])
                show_success("Owner deleted successfully")
                load_owners()
                dlg.open = False
                page.update()
            except Exception as ex:
                show_error(f"Error: {str(ex)}")
        
        dlg.title = ft.Text("Confirm Delete")
        dlg.content = ft.Text(f"Delete '{owner.get('name', '')}'?")
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
                ft.Text("Add New Owner", size=16, weight="bold"),
                create_form_field_row("Name", name_field),
                create_form_field_row("Phone", phone_field),
                create_form_field_row("Legal ID", legal_id_field),
                create_form_field_row("Family Count", family_count_field),
                ft.Row(
                    controls=[
                        ft.ElevatedButton(
                            "Save",
                            icon=icons.SAVE,
                            on_click=add_owner,
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
    load_owners()
    
    content = ft.Column(
        controls=[
            create_header("Owners", "Manage property owners"),
            ft.ElevatedButton(
                "Add Owner",
                icon=icons.ADD,
                on_click=lambda e: setattr(form_container, 'visible', not form_container.visible) or page.update(),
            ),
            form_container,
            ft.Container(
                content=ft.Text("Owners List", size=16, weight="bold"),
                margin=ft.margin.only(top=20),
            ),
            owners_table,
        ],
        spacing=16,
        scroll=ft.ScrollMode.AUTO,
    )
    
    return content
