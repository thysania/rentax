import flet as ft
from flet import icons
from gui.components.common import create_header, create_text_field, create_form_field_row
from services import unit_service, owner_service, client_service


def create(page: ft.Page):
    """Create ownerships management page"""
    
    # Dialog and snackbar
    dlg = ft.AlertDialog()
    page.dialog = dlg
    
    snackbar = ft.SnackBar(ft.Text(""))
    page.overlay.append(snackbar)
    
    # State for editing
    editing_ownership = {"id": None}
    
    # Form fields
    unit_dropdown = ft.Dropdown(
        label="Select Unit",
        border_radius=6,
    )
    
    owner_dropdown = ft.Dropdown(
        label="Select Owner",
        border_radius=6,
    )
    
    share_percent_field = create_text_field("Ownership Share %", "e.g., 50")
    
    alternating_toggle = ft.Checkbox(
        label="Alternating Ownership (seasonal or monthly split)",
        on_change=lambda e: update_alternating_visibility(),
    )
    
    odd_even_dropdown = ft.Dropdown(
        label="Owner Controls",
        options=[
            ft.dropdown.Option("odd", text="Odd Months (1,3,5,7,9,11)"),
            ft.dropdown.Option("even", text="Even Months (2,4,6,8,10,12)"),
        ],
        border_radius=6,
        visible=False,
    )
    
    # Data table
    ownerships_table = ft.Column(controls=[], spacing=8)
    
    def load_dropdowns():
        """Load units and owners into dropdowns"""
        try:
            units = unit_service.list_all_units() or []
            owners = owner_service.list_all_owners() or []
            
            unit_options = [
                ft.dropdown.Option(
                    str(u['id']),
                    text=f"{u.get('reference', '')} - {u.get('city', '')}",
                )
                for u in units
            ]
            owner_options = [
                ft.dropdown.Option(str(o['id']), text=o.get('name', ''))
                for o in owners
            ]
            
            unit_dropdown.options = unit_options or [ft.dropdown.Option("", text="No units")]
            owner_dropdown.options = owner_options or [ft.dropdown.Option("", text="No owners")]
            page.update()
        except Exception as e:
            show_error(f"Error loading data: {str(e)}")
    
    def update_alternating_visibility():
        """Show/hide odd_even dropdown based on toggle"""
        odd_even_dropdown.visible = alternating_toggle.value
        page.update()
    
    def load_ownerships():
        """Load ownerships into table"""
        try:
            ownerships = unit_service.list_all_ownerships() or []
            units = {u['id']: u for u in (unit_service.list_all_units() or [])}
            owners = {o['id']: o for o in (owner_service.list_all_owners() or [])}
            
            rows = []
            for own in ownerships:
                unit = units.get(own.get('unit_id'), {})
                owner = owners.get(own.get('owner_id'), {})
                
                alternating_text = ""
                if own.get('is_alternating'):
                    alternating_text = f" ({own.get('odd_even', 'N/A')} months)"
                
                rows.append(
                    ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text(str(own.get('id', '')))),
                            ft.DataCell(ft.Text(unit.get('reference', 'N/A'))),
                            ft.DataCell(ft.Text(owner.get('name', 'N/A'))),
                            ft.DataCell(ft.Text(f"{own.get('share_percent', 0)}%")),
                            ft.DataCell(ft.Text(alternating_text or "Fixed")),
                            ft.DataCell(
                                ft.Row(
                                    controls=[
                                        ft.IconButton(
                                            icon=icons.EDIT,
                                            icon_size=18,
                                            on_click=lambda e, o=own: edit_ownership(o),
                                        ),
                                        ft.IconButton(
                                            icon=icons.DELETE,
                                            icon_size=18,
                                            on_click=lambda e, o=own: delete_ownership(o),
                                        ),
                                    ],
                                    spacing=4,
                                )
                            ),
                        ]
                    )
                )
            
            ownerships_table.controls = [
                ft.DataTable(
                    columns=[
                        ft.DataColumn(ft.Text("ID", weight="w500")),
                        ft.DataColumn(ft.Text("Unit", weight="w500")),
                        ft.DataColumn(ft.Text("Owner", weight="w500")),
                        ft.DataColumn(ft.Text("Share %", weight="w500")),
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
            show_error(f"Error loading ownerships: {str(e)}")
    
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
        owner_dropdown.value = None
        share_percent_field.value = ""
        alternating_toggle.value = False
        odd_even_dropdown.value = None
        odd_even_dropdown.visible = False
        editing_ownership["id"] = None
    
    def add_ownership(e):
        """Add new ownership"""
        if not unit_dropdown.value:
            show_error("Unit is required")
            return
        if not owner_dropdown.value:
            show_error("Owner is required")
            return
        if not share_percent_field.value:
            show_error("Share percentage is required")
            return
        
        try:
            share = float(share_percent_field.value)
            if share < 0 or share > 100:
                show_error("Share must be between 0 and 100")
                return
            
            unit_service.create_ownership(
                unit_id=int(unit_dropdown.value),
                owner_id=int(owner_dropdown.value),
                share_percent=share,
                is_alternating=alternating_toggle.value,
                odd_even=odd_even_dropdown.value if alternating_toggle.value else None,
            )
            show_success("Ownership created successfully")
            clear_form()
            load_ownerships()
            form_container.visible = False
            page.update()
        except Exception as ex:
            show_error(f"Error: {str(ex)}")
    
    def edit_ownership(own):
        """Edit ownership"""
        editing_ownership["id"] = own['id']
        unit_dropdown.value = str(own.get('unit_id', ''))
        owner_dropdown.value = str(own.get('owner_id', ''))
        share_percent_field.value = str(own.get('share_percent', ''))
        alternating_toggle.value = bool(own.get('is_alternating', False))
        odd_even_dropdown.value = own.get('odd_even', None)
        update_alternating_visibility()
        form_container.visible = True
        page.update()
    
    def delete_ownership(own):
        """Delete ownership"""
        def confirm():
            try:
                unit_service.delete_ownership(own['id'])
                show_success("Ownership deleted successfully")
                load_ownerships()
                dlg.open = False
                page.update()
            except Exception as ex:
                show_error(f"Error: {str(ex)}")
        
        dlg.title = ft.Text("Confirm Delete")
        dlg.content = ft.Text("Delete this ownership record?")
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
                ft.Text("Add Ownership", size=16, weight="bold"),
                create_form_field_row("Unit", unit_dropdown),
                create_form_field_row("Owner", owner_dropdown),
                create_form_field_row("Share %", share_percent_field),
                ft.Container(
                    content=alternating_toggle,
                    padding=ft.padding.only(left=12, right=12),
                ),
                ft.Container(
                    content=odd_even_dropdown,
                    visible=False,
                    padding=ft.padding.only(left=12, right=12),
                    expand=True,
                ),
                ft.Row(
                    controls=[
                        ft.ElevatedButton(
                            "Save",
                            icon=icons.SAVE,
                            on_click=add_ownership,
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
    
    # Bind odd_even_dropdown visibility to toggle
    odd_even_dropdown.parent = form_container
    
    # Main content
    load_dropdowns()
    load_ownerships()
    
    content = ft.Column(
        controls=[
            create_header("Ownerships", "Manage unit ownership shares"),
            ft.ElevatedButton(
                "Add Ownership",
                icon=icons.ADD,
                on_click=lambda e: setattr(form_container, 'visible', not form_container.visible) or page.update(),
            ),
            form_container,
            ft.Container(
                content=ft.Text("Ownerships List", size=16, weight="bold"),
                margin=ft.margin.only(top=20),
            ),
            ownerships_table,
        ],
        spacing=16,
        scroll=ft.ScrollMode.AUTO,
    )
    
    return content
