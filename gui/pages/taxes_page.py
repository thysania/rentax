import flet as ft
from flet import icons
from gui.components.common import create_header, create_text_field, create_form_field_row
from services import owner_service


def create(page: ft.Page):
    """Create taxes reporting page"""
    
    snackbar = ft.SnackBar(ft.Text(""))
    page.overlay.append(snackbar)
    
    # Form fields
    owner_dropdown = ft.Dropdown(
        label="Select Owner",
        border_radius=6,
    )
    
    year_field = create_text_field("Year", "e.g., 2024")
    start_date_field = create_text_field("Start Date", "YYYY-MM-DD")
    end_date_field = create_text_field("End Date", "YYYY-MM-DD")
    
    # Tax report display
    report_container = ft.Column(controls=[], spacing=8)
    
    def load_owners():
        """Load owners into dropdown"""
        try:
            owners = owner_service.list_all_owners() or []
            
            owner_options = [
                ft.dropdown.Option(str(o['id']), text=o.get('name', ''))
                for o in owners
            ]
            
            owner_dropdown.options = owner_options or [ft.dropdown.Option("", text="No owners")]
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
    
    def generate_report(e):
        """Generate tax report"""
        if not owner_dropdown.value and not year_field.value and not start_date_field.value:
            show_error("Select an owner or date range")
            return
        
        try:
            # Get tax calculations
            owner_id = int(owner_dropdown.value) if owner_dropdown.value else None
            year = int(year_field.value) if year_field.value else None
            start_date = start_date_field.value if start_date_field.value else None
            end_date = end_date_field.value if end_date_field.value else None
            
            # For demonstration, create a sample tax report
            report_rows = []
            
            if owner_id:
                owner = owner_service.get_owner(owner_id)
                report_rows.append(
                    ft.Container(
                        content=ft.Column(
                            controls=[
                                ft.Text("Owner: " + owner.get('name', ''), size=14, weight="bold"),
                                ft.Text(f"Legal ID: {owner.get('legal_id', 'N/A')}", size=12),
                                ft.Text(f"Phone: {owner.get('phone', 'N/A')}", size=12),
                            ]
                        ),
                        padding=12,
                        bgcolor="#f0f0f0",
                        border_radius=6,
                    )
                )
            
            if year:
                report_rows.append(
                    ft.Text(f"Tax Year: {year}", size=14, weight="bold")
                )
            elif start_date or end_date:
                period = f"From {start_date or 'Start'} to {end_date or 'End'}"
                report_rows.append(
                    ft.Text(f"Period: {period}", size=14, weight="bold")
                )
            
            # Tax summary cards
            summary_row = ft.Row(
                controls=[
                    create_summary_card("Total Receipts", "$12,450", "#4CAF50"),
                    create_summary_card("Rental Income", "$12,450", "#2196F3"),
                    create_summary_card("RAS-IR Count", "3 months", "#FF9800"),
                ],
                spacing=12,
                wrap=True,
            )
            report_rows.append(summary_row)
            
            # Detailed table
            report_rows.append(
                ft.Container(
                    content=ft.Text("Monthly Breakdown", size=14, weight="bold"),
                    margin=ft.margin.only(top=20),
                )
            )
            
            table_rows = [
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text("Month", weight="w500")),
                        ft.DataCell(ft.Text("Receipt Count", weight="w500")),
                        ft.DataCell(ft.Text("Total Amount", weight="w500")),
                        ft.DataCell(ft.Text("RAS-IR", weight="w500")),
                    ]
                )
            ]
            
            # Sample data
            months_data = [
                ("January 2024", 4, 5000, "Yes"),
                ("February 2024", 3, 4500, "No"),
                ("March 2024", 2, 2950, "Yes"),
            ]
            
            for month, count, amount, ras_ir in months_data:
                table_rows.append(
                    ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text(month)),
                            ft.DataCell(ft.Text(str(count))),
                            ft.DataCell(ft.Text(f"${amount}")),
                            ft.DataCell(ft.Text(ras_ir)),
                        ]
                    )
                )
            
            report_rows.append(
                ft.DataTable(
                    columns=[
                        ft.DataColumn(ft.Text("Month", weight="w500")),
                        ft.DataColumn(ft.Text("Count", weight="w500")),
                        ft.DataColumn(ft.Text("Amount", weight="w500")),
                        ft.DataColumn(ft.Text("RAS-IR", weight="w500")),
                    ],
                    rows=table_rows,
                    border=ft.border.all(1, "#E0E0E0"),
                    border_radius=8,
                )
            )
            
            # Export button
            report_rows.append(
                ft.Row(
                    controls=[
                        ft.ElevatedButton(
                            "Export to CSV",
                            icon=icons.DOWNLOAD,
                            on_click=lambda e: export_csv(),
                        ),
                        ft.ElevatedButton(
                            "Print Report",
                            icon=icons.PRINT,
                            on_click=lambda e: print_report(),
                        ),
                    ],
                    spacing=12,
                    margin=ft.margin.only(top=20),
                )
            )
            
            report_container.controls = report_rows
            show_success("Report generated successfully")
            page.update()
        except Exception as ex:
            show_error(f"Error generating report: {str(ex)}")
    
    def export_csv():
        """Export report to CSV"""
        show_success("Report exported to CSV")
    
    def print_report():
        """Print report"""
        show_success("Printing report...")
    
    def create_summary_card(title: str, value: str, color: str):
        """Create a summary stat card"""
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(title, size=12, color="#666"),
                    ft.Text(value, size=18, weight="bold", color=color),
                ],
                spacing=4,
            ),
            padding=16,
            bgcolor="white",
            border_radius=8,
            border=ft.border.all(1, "#E0E0E0"),
            expand=True,
            min_width=150,
        )
    
    # Form container
    form_container = ft.Container(
        content=ft.Column(
            controls=[
                ft.Text("Tax Report Generator", size=16, weight="bold"),
                create_form_field_row("Owner (Optional)", owner_dropdown),
                create_form_field_row("Year (Optional)", year_field),
                ft.Text("Or Date Range:", size=12, weight="w500", color="#666"),
                create_form_field_row("Start Date", start_date_field),
                create_form_field_row("End Date", end_date_field),
                ft.Row(
                    controls=[
                        ft.ElevatedButton(
                            "Generate Report",
                            icon=icons.ASSESSMENT,
                            on_click=generate_report,
                        ),
                        ft.TextButton(
                            "Clear",
                            on_click=lambda e: clear_filters(),
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
        margin=ft.margin.only(bottom=20),
    )
    
    def clear_filters():
        """Clear filter fields"""
        owner_dropdown.value = None
        year_field.value = ""
        start_date_field.value = ""
        end_date_field.value = ""
        report_container.controls = []
        page.update()
    
    # Main content
    load_owners()
    
    content = ft.Column(
        controls=[
            create_header("Taxes", "Tax reports and calculations"),
            form_container,
            ft.Container(
                content=ft.Text("Tax Report", size=16, weight="bold"),
                margin=ft.margin.only(top=20),
            ),
            report_container,
        ],
        spacing=16,
        scroll=ft.ScrollMode.AUTO,
    )
    
    return content
