import flet as ft
from flet import icons
from gui.components.common import create_header, create_text_field, create_form_field_row
from services import assignment_service, unit_service, client_service


def create(page: ft.Page):
    """Create assignments management page"""
    
    # Dialog and snackbar
    dlg = ft.AlertDialog()
    page.dialog = dlg
    
    snackbar = ft.SnackBar(ft.Text(""))
    page.overlay.append(snackbar)
    
    # Form fields
    unit_dropdown = ft.Dropdown(
        label="Select Unit",
        border_radius=6,
    )
    
    client_dropdown = ft.Dropdown(
        label="Select Client",
        border_radius=6,
    )
    
    start_date_field = create_text_field("Start Date", "YYYY-MM-DD")
    end_date_field = create_text_field("End Date", "YYYY-MM-DD")
    rent_amount_field = create_text_field("Monthly Rent Amount", "e.g., 1000")
    
    ras_ir_toggle = ft.Checkbox(label="RAS-IR Tax (rent as income)")
    
    # Data table
    assignments_table = ft.Column(controls=[], spacing=8)
    
    def load_dropdowns():
        """Load units and clients into dropdowns"""
        try:
            units = unit_service.list_all_units() or []
            clients = client_service.list_all_clients() or []
            
            unit_options = [
                ft.dropdown.Option(
                    str(u['id']),
                    text=f"{u.get('reference', '')} - {u.get('city', '')}",
                )
                for u in units
            ]
            client_options = [
                ft.dropdown.Option(str(c['id']), text=c.get('name', ''))
                for c in clients
            ]
            
            unit_dropdown.options = unit_options or [ft.dropdown.Option("", text="No units")]
            client_dropdown.options = client_options or [ft.dropdown.Option("", text="No clients")]
            page.update()
        except Exception as e:
            show_error(f"Error loading data: {str(e)}")
    
    def load_assignments():
        """Load assignments into table"""
        try:
            assignments = assignment_service.list_all_assignments() or []
            units = {u['id']: u for u in (unit_service.list_all_units() or [])}
            clients = {c['id']: c for c in (client_service.list_all_clients() or [])}
            
            rows = []
            for assign in assignments:
                unit = units.get(assign.get('unit_id'), {})
                client = clients.get(assign.get('client_id'), {})
                
                rows.append(
                    ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text(str(assign.get('id', '')))),
                            ft.DataCell(ft.Text(unit.get('reference', 'N/A'))),
                            ft.DataCell(ft.Text(client.get('name', 'N/A'))),
                            ft.DataCell(ft.Text(assign.get('start_date', ''))),
                            ft.DataCell(ft.Text(assign.get('end_date', '') or "Ongoing")),
                            ft.DataCell(ft.Text(f"${assign.get('rent_amount', 0)}")),
                            ft.DataCell(
                                ft.Row(
                                    controls=[
                                        ft.IconButton(
                                            icon=icons.EDIT,
                                            icon_size=18,
                                            on_click=lambda e, a=assign: edit_assignment(a),
                                        ),
                                        ft.IconButton(
                                            icon=icons.DELETE,
                                            icon_size=18,
                                            on_click=lambda e, a=assign: delete_assignment(a),
                                        ),
                                    ],
                                    spacing=4,
                                )
                            ),
                        ]
                    )
                )
            
            assignments_table.controls = [
                ft.DataTable(
                    columns=[
                        ft.DataColumn(ft.Text("ID", weight="w500")),
                        ft.DataColumn(ft.Text("Unit", weight="w500")),
                        ft.DataColumn(ft.Text("Client", weight="w500")),
                        ft.DataColumn(ft.Text("Start", weight="w500")),
                        ft.DataColumn(ft.Text("End", weight="w500")),
                        ft.DataColumn(ft.Text("Rent", weight="w500")),
                        ft.DataColumn(ft.Text("Actions", weight="w500")),
                    ],
                    rows=rows,
                    border=ft.border.all(1, "#E0E0E0"),
                    border_radius=8,
                )
            ]
            page.update()
        except Exception as e:
            show_error(f"Error loading assignments: {str(e)}")
    
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
        unit_dropdown.value = None
        client_dropdown.value = None
        start_date_field.value = ""
        end_date_field.value = ""
        rent_amount_field.value = ""
        ras_ir_toggle.value = False
    
    def add_assignment(e):
        """Add new assignment"""
        if not unit_dropdown.value:
            show_error("Unit is required")
            return
        if not client_dropdown.value:
            show_error("Client is required")
            return
        if not start_date_field.value:
            show_error("Start date is required")
            return
        if not rent_amount_field.value:
            show_error("Rent amount is required")
            return
        
        try:
            rent = float(rent_amount_field.value)
            assignment_service.create_assignment(
                unit_id=int(unit_dropdown.value),
                client_id=int(client_dropdown.value),
                start_date=start_date_field.value,
                end_date=end_date_field.value or None,
                rent_amount=rent,
                ras_ir=ras_ir_toggle.value,
            )
            show_success("Assignment created successfully")
            clear_form()
            load_assignments()
            form_container.visible = False
            page.update()
        except Exception as ex:
            show_error(f"Error: {str(ex)}")
    
    def edit_assignment(assign):
        """Edit assignment"""
        unit_dropdown.value = str(assign.get('unit_id', ''))
        client_dropdown.value = str(assign.get('client_id', ''))
        start_date_field.value = assign.get('start_date', '')
        end_date_field.value = assign.get('end_date', '')
        rent_amount_field.value = str(assign.get('rent_amount', ''))
        ras_ir_toggle.value = bool(assign.get('ras_ir', False))
        form_container.visible = True
        page.update()
    
    def delete_assignment(assign):
        """Delete assignment"""
        def confirm():
            try:
                assignment_service.delete_assignment(assign['id'])
                show_success("Assignment deleted successfully")
                load_assignments()
                dlg.open = False
                page.update()
            except Exception as ex:
                show_error(f"Error: {str(ex)}")
        
        dlg.title = ft.Text("Confirm Delete")
        dlg.content = ft.Text("Delete this assignment/contract?")
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
                ft.Text("Add Assignment", size=16, weight="bold"),
                create_form_field_row("Unit", unit_dropdown),
                create_form_field_row("Client", client_dropdown),
                create_form_field_row("Start Date", start_date_field),
                create_form_field_row("End Date", end_date_field),
                create_form_field_row("Monthly Rent", rent_amount_field),
                ft.Container(
                    content=ras_ir_toggle,
                    padding=ft.padding.only(left=12, right=12),
                ),
                ft.Row(
                    controls=[
                        ft.ElevatedButton(
                            "Save",
                            icon=icons.SAVE,
                            on_click=add_assignment,
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
    load_assignments()
    
    content = ft.Column(
        controls=[
            create_header("Assignments", "Manage rental contracts"),
            ft.ElevatedButton(
                "Add Assignment",
                icon=icons.ADD,
                on_click=lambda e: setattr(form_container, 'visible', not form_container.visible) or page.update(),
            ),
            form_container,
            ft.Container(
                content=ft.Text("Assignments List", size=16, weight="bold"),
                margin=ft.margin.only(top=20),
            ),
            assignments_table,
        ],
        spacing=16,
        scroll=ft.ScrollMode.AUTO,
    )
    
    return content
