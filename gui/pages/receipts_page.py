import flet as ft
from flet import icons
from gui.components.common import create_header, create_text_field, create_form_field_row
from services import receipt_service, assignment_service, owner_service


def create(page: ft.Page):
    """Create receipts management page"""
    
    # Dialog and snackbar
    dlg = ft.AlertDialog()
    page.dialog = dlg
    
    snackbar = ft.SnackBar(ft.Text(""))
    page.overlay.append(snackbar)
    
    # Form fields
    assignment_dropdown = ft.Dropdown(
        label="Select Assignment",
        border_radius=6,
    )
    
    owner_dropdown = ft.Dropdown(
        label="Select Owner (for payment)",
        border_radius=6,
    )
    
    period_field = create_text_field("Period (Month)", "YYYY-MM-01")
    created_at_field = create_text_field("Payment Date", "YYYY-MM-DD")
    amount_field = create_text_field("Payment Amount", "e.g., 1000")
    
    # Data table
    receipts_table = ft.Column(controls=[], spacing=8)
    
    def load_dropdowns():
        """Load assignments and owners into dropdowns"""
        try:
            assignments = assignment_service.list_all_assignments() or []
            owners = owner_service.list_all_owners() or []
            
            assign_options = [
                ft.dropdown.Option(
                    str(a['id']),
                    text=f"Assignment {a.get('id', '')} - Unit {a.get('unit_id', '')}",
                )
                for a in assignments
            ]
            owner_options = [
                ft.dropdown.Option(str(o['id']), text=o.get('name', ''))
                for o in owners
            ]
            
            assignment_dropdown.options = assign_options or [ft.dropdown.Option("", text="No assignments")]
            owner_dropdown.options = owner_options or [ft.dropdown.Option("", text="No owners")]
            page.update()
        except Exception as e:
            show_error(f"Error loading data: {str(e)}")
    
    def load_receipts():
        """Load receipts into table"""
        try:
            receipts = receipt_service.list_all_receipts() or []
            assignments = {a['id']: a for a in (assignment_service.list_all_assignments() or [])}
            owners = {o['id']: o for o in (owner_service.list_all_owners() or [])}
            
            rows = []
            for receipt in receipts:
                assignment = assignments.get(receipt.get('assignment_id'), {})
                owner = owners.get(receipt.get('owner_id'), {})
                
                rows.append(
                    ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text(str(receipt.get('id', '')))),
                            ft.DataCell(ft.Text(str(assignment.get('id', 'N/A')))),
                            ft.DataCell(ft.Text(owner.get('name', 'N/A'))),
                            ft.DataCell(ft.Text(receipt.get('period', ''))),
                            ft.DataCell(ft.Text(receipt.get('created_at', ''))),
                            ft.DataCell(ft.Text(f"${receipt.get('amount', 0)}")),
                            ft.DataCell(
                                ft.Row(
                                    controls=[
                                        ft.IconButton(
                                            icon=icons.EDIT,
                                            icon_size=18,
                                            on_click=lambda e, r=receipt: edit_receipt(r),
                                        ),
                                        ft.IconButton(
                                            icon=icons.DELETE,
                                            icon_size=18,
                                            on_click=lambda e, r=receipt: delete_receipt(r),
                                        ),
                                    ],
                                    spacing=4,
                                )
                            ),
                        ]
                    )
                )
            
            receipts_table.controls = [
                ft.DataTable(
                    columns=[
                        ft.DataColumn(ft.Text("ID", weight="w500")),
                        ft.DataColumn(ft.Text("Assignment", weight="w500")),
                        ft.DataColumn(ft.Text("Owner", weight="w500")),
                        ft.DataColumn(ft.Text("Period", weight="w500")),
                        ft.DataColumn(ft.Text("Date", weight="w500")),
                        ft.DataColumn(ft.Text("Amount", weight="w500")),
                        ft.DataColumn(ft.Text("Actions", weight="w500")),
                    ],
                    rows=rows,
                    border=ft.border.all(1, "#E0E0E0"),
                    border_radius=8,
                )
            ]
            page.update()
        except Exception as e:
            show_error(f"Error loading receipts: {str(e)}")
    
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
        assignment_dropdown.value = None
        owner_dropdown.value = None
        period_field.value = ""
        created_at_field.value = ""
        amount_field.value = ""
    
    def add_receipt(e):
        """Add new receipt"""
        if not assignment_dropdown.value:
            show_error("Assignment is required")
            return
        if not owner_dropdown.value:
            show_error("Owner is required")
            return
        if not period_field.value:
            show_error("Period is required")
            return
        if not created_at_field.value:
            show_error("Payment date is required")
            return
        if not amount_field.value:
            show_error("Amount is required")
            return
        
        try:
            amount = float(amount_field.value)
            receipt_service.create_receipt(
                assignment_id=int(assignment_dropdown.value),
                owner_id=int(owner_dropdown.value),
                period=period_field.value,
                created_at=created_at_field.value,
                amount=amount,
            )
            show_success("Receipt created successfully")
            clear_form()
            load_receipts()
            form_container.visible = False
            page.update()
        except Exception as ex:
            show_error(f"Error: {str(ex)}")
    
    def edit_receipt(receipt):
        """Edit receipt"""
        assignment_dropdown.value = str(receipt.get('assignment_id', ''))
        owner_dropdown.value = str(receipt.get('owner_id', ''))
        period_field.value = receipt.get('period', '')
        created_at_field.value = receipt.get('created_at', '')
        amount_field.value = str(receipt.get('amount', ''))
        form_container.visible = True
        page.update()
    
    def delete_receipt(receipt):
        """Delete receipt"""
        def confirm():
            try:
                receipt_service.delete_receipt(receipt['id'])
                show_success("Receipt deleted successfully")
                load_receipts()
                dlg.open = False
                page.update()
            except Exception as ex:
                show_error(f"Error: {str(ex)}")
        
        dlg.title = ft.Text("Confirm Delete")
        dlg.content = ft.Text("Delete this receipt?")
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
                ft.Text("Add Receipt", size=16, weight="bold"),
                create_form_field_row("Assignment", assignment_dropdown),
                create_form_field_row("Owner", owner_dropdown),
                create_form_field_row("Period", period_field),
                create_form_field_row("Payment Date", created_at_field),
                create_form_field_row("Amount", amount_field),
                ft.Row(
                    controls=[
                        ft.ElevatedButton(
                            "Save",
                            icon=icons.SAVE,
                            on_click=add_receipt,
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
    load_dropdowns()
    load_receipts()
    
    content = ft.Column(
        controls=[
            create_header("Receipts", "Manage receipts and payments"),
            ft.ElevatedButton(
                "Add Receipt",
                icon=icons.ADD,
                on_click=lambda e: setattr(form_container, 'visible', not form_container.visible) or page.update(),
            ),
            form_container,
            ft.Container(
                content=ft.Text("Receipts List", size=16, weight="bold"),
                margin=ft.margin.only(top=20),
            ),
            receipts_table,
        ],
        spacing=16,
        scroll=ft.ScrollMode.AUTO,
    )
    
    return content
