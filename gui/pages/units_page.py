import flet as ft
from flet import icons
from gui.components.common import create_header, create_text_field, create_form_field_row
from services import unit_service


def create(page: ft.Page):
    """Create units management page"""
    
    # Dialog and snackbar
    dlg = ft.AlertDialog()
    page.dialog = dlg
    
    snackbar = ft.SnackBar(ft.Text(""))
    page.overlay.append(snackbar)
    
    # Form fields
    reference_field = create_text_field("Unit Reference", "e.g., APT-101")
    city_field = create_text_field("City", "e.g., New York")
    neighborhood_field = create_text_field("Neighborhood", "Optional")
    floor_field = create_text_field("Floor", "e.g., 3")
    unit_type_field = create_text_field("Unit Type", "apt, store, building")
    
    # Data table
    units_table = ft.Column(controls=[], spacing=8)
    
    def load_units():
        """Load units into table"""
        try:
            units = unit_service.list_all_units() or []
            
            rows = []
            for unit in units:
                rows.append(
                    ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text(str(unit.get('id', '')))),
                            ft.DataCell(ft.Text(unit.get('reference', ''))),
                            ft.DataCell(ft.Text(unit.get('city', 'N/A'))),
                            ft.DataCell(ft.Text(unit.get('neighborhood', 'N/A'))),
                            ft.DataCell(ft.Text(str(unit.get('floor', 'N/A')))),
                            ft.DataCell(ft.Text(unit.get('unit_type', 'N/A'))),
                            ft.DataCell(
                                ft.Row(
                                    controls=[
                                        ft.IconButton(
                                            icon=icons.EDIT,
                                            icon_size=18,
                                            on_click=lambda e, u=unit: edit_unit(u),
                                        ),
                                        ft.IconButton(
                                            icon=icons.DELETE,
                                            icon_size=18,
                                            on_click=lambda e, u=unit: delete_unit(u),
                                        ),
                                    ],
                                    spacing=4,
                                )
                            ),
                        ]
                    )
                )
            
            units_table.controls = [
                ft.DataTable(
                    columns=[
                        ft.DataColumn(ft.Text("ID", weight="w500")),
                        ft.DataColumn(ft.Text("Reference", weight="w500")),
                        ft.DataColumn(ft.Text("City", weight="w500")),
                        ft.DataColumn(ft.Text("Neighborhood", weight="w500")),
                        ft.DataColumn(ft.Text("Floor", weight="w500")),
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
            show_error(f"Error loading units: {str(e)}")
    
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
        reference_field.value = ""
        city_field.value = ""
        neighborhood_field.value = ""
        floor_field.value = ""
        unit_type_field.value = ""
    
    def add_unit(e):
        """Add new unit"""
        if not reference_field.value:
            show_error("Reference is required")
            return
        
        try:
            unit_service.create_unit(
                reference=reference_field.value,
                city=city_field.value or None,
                neighborhood=neighborhood_field.value or None,
                floor=int(floor_field.value) if floor_field.value else None,
                unit_type=unit_type_field.value or None,
            )
            show_success("Unit added successfully")
            clear_form()
            load_units()
            form_container.visible = False
            page.update()
        except Exception as ex:
            show_error(f"Error: {str(ex)}")
    
    def edit_unit(unit):
        """Edit unit"""
        reference_field.value = unit.get('reference', '')
        city_field.value = unit.get('city', '')
        neighborhood_field.value = unit.get('neighborhood', '')
        floor_field.value = str(unit.get('floor', ''))
        unit_type_field.value = unit.get('unit_type', '')
        form_container.visible = True
        page.update()
    
    def delete_unit(unit):
        """Delete unit"""
        def confirm():
            try:
                unit_service.delete_unit(unit['id'])
                show_success("Unit deleted successfully")
                load_units()
                dlg.open = False
                page.update()
            except Exception as ex:
                show_error(f"Error: {str(ex)}")
        
        dlg.title = ft.Text("Confirm Delete")
        dlg.content = ft.Text(f"Delete '{unit.get('reference', '')}'?")
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
                ft.Text("Add New Unit", size=16, weight="bold"),
                create_form_field_row("Reference", reference_field),
                create_form_field_row("City", city_field),
                create_form_field_row("Neighborhood", neighborhood_field),
                create_form_field_row("Floor", floor_field),
                create_form_field_row("Unit Type", unit_type_field),
                ft.Row(
                    controls=[
                        ft.ElevatedButton(
                            "Save",
                            icon=icons.SAVE,
                            on_click=add_unit,
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
    load_units()
    
    content = ft.Column(
        controls=[
            create_header("Units", "Manage rental units"),
            ft.ElevatedButton(
                "Add Unit",
                icon=icons.ADD,
                on_click=lambda e: setattr(form_container, 'visible', not form_container.visible) or page.update(),
            ),
            form_container,
            ft.Container(
                content=ft.Text("Units List", size=16, weight="bold"),
                margin=ft.margin.only(top=20),
            ),
            units_table,
        ],
        spacing=16,
        scroll=ft.ScrollMode.AUTO,
    )
    
    return content
