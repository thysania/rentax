import flet as ft
from flet import icons
from gui.components.common import create_header, create_stat_card
from services import owner_service, unit_service, client_service
from services.assignment_service import list_assignments
from services.receipt_service import list_receipt_logs_with_names


def create(page: ft.Page):
    """Create dashboard page"""
    
    def load_stats():
        """Load statistics"""
        try:
            owners_count = len(owner_service.list_owners() or [])
            units_count = len(unit_service.list_all_units() or [])
            clients_count = len(client_service.list_all_clients() or [])
            assignments_count = len(list_assignments() or [])
            
            return owners_count, units_count, clients_count, assignments_count
        except:
            return 0, 0, 0, 0
    
    # Load initial stats
    owners_count, units_count, clients_count, assignments_count = load_stats()
    
    # Create stat cards
    stat_cards = ft.Row(
        controls=[
            create_stat_card("Total Owners", str(owners_count), icons.PERSON, "#2E86AB"),
            create_stat_card("Total Units", str(units_count), icons.HOME, "#A23B72"),
            create_stat_card("Total Clients", str(clients_count), icons.PEOPLE, "#F4A460"),
            create_stat_card("Active Assignments", str(assignments_count), icons.DESCRIPTION, "#4CAF50"),
        ],
        spacing=16,
        wrap=True,
    )
    
    # Recent receipts section
    def get_recent_receipts():
        try:
            receipts = list_receipt_logs_with_names()
            return receipts[-5:] if receipts else []
        except:
            return []
    
    recent_receipts = get_recent_receipts()
    
    recent_receipts_list = ft.Column(
        controls=[
            ft.Row(
                controls=[
                    ft.Container(
                        content=ft.Text(
                            f"#{r.get('uid', 'N/A')} - {r.get('unit_reference', 'N/A')}",
                            size=12,
                            weight="w500"
                        ),
                        width=150,
                    ),
                    ft.Container(
                        content=ft.Text(
                            f"{r.get('owner_name', 'N/A')}",
                            size=12,
                        ),
                        width=150,
                    ),
                    ft.Container(
                        content=ft.Text(
                            f"${r.get('amount', 0):.2f}",
                            size=12,
                            weight="w500",
                        ),
                        expand=True,
                        alignment=ft.alignment.center_right,
                    ),
                ],
                spacing=16,
                height=40,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            )
            for r in recent_receipts
        ],
        spacing=8,
    ) if recent_receipts else ft.Text("No recent receipts", color="#999", size=12)
    
    # Main dashboard content
    content = ft.Column(
        controls=[
            create_header("Dashboard", "Welcome to Rent Manager"),
            stat_cards,
            ft.Divider(height=30),
            ft.Text("Recent Receipts", size=18, weight="bold", color="#333"),
            ft.Container(
                content=recent_receipts_list,
                padding=16,
                bgcolor="white",
                border_radius=8,
                border=ft.border.all(1, "#E0E0E0"),
            ),
        ],
        spacing=20,
        scroll=ft.ScrollMode.AUTO,
    )
    
    return content
