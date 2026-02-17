import flet as ft
from flet import icons
from database import initialize_database
from gui.pages import (
    dashboard_page,
    owners_page,
    units_page,
    clients_page,
    ownerships_page,
    assignments_page,
    receipts_page,
    taxes_page,
)


def main(page: ft.Page):
    page.title = "Rent Manager"
    page.window.width = 1400
    page.window.height = 900
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0
    page.scroll = ft.ScrollMode.AUTO

    # Initialize database
    initialize_database()

    # Color scheme
    primary_color = "#2E86AB"  # Professional blue
    secondary_color = "#A23B72"  # Purple accent
    light_bg = "#F8F9FA"  # Light gray background
    white = "#FFFFFF"

    page.theme = ft.Theme(
        color_scheme=ft.ColorScheme(
            primary="#2E86AB",
            secondary="#A23B72",
            surface="#F8F9FA",
        ),
        use_material3=True,
    )

    # Dictionary to store page references
    pages_dict = {}

    def create_nav_item(icon: str, label: str, page_key: str):
        """Create a navigation item"""
        return ft.Container(
            content=ft.Row(
                controls=[
                    ft.Icon(icon, size=20, color=primary_color),
                    ft.Text(label, size=14, weight="w500"),
                ],
                spacing=12,
                height=45,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.padding.symmetric(10, 12),
            border_radius=8,
            on_click=lambda e: show_page(page_key),
            mouse_cursor=ft.MouseCursor.POINTER,
            ink=True,
        )

    def show_page(page_key: str):
        """Show the selected page"""
        # Hide all pages
        for key, page_obj in pages_dict.items():
            page_obj.visible = False

        # Show selected page
        if page_key in pages_dict:
            pages_dict[page_key].visible = True

        # Update page content
        page.update()

    # Create pages
    pages_dict["dashboard"] = dashboard_page.create(page)
    pages_dict["owners"] = owners_page.create(page)
    pages_dict["units"] = units_page.create(page)
    pages_dict["clients"] = clients_page.create(page)
    pages_dict["ownerships"] = ownerships_page.create(page)
    pages_dict["assignments"] = assignments_page.create(page)
    pages_dict["receipts"] = receipts_page.create(page)
    pages_dict["taxes"] = taxes_page.create(page)

    # Initially hide all pages
    for page_obj in pages_dict.values():
        page_obj.visible = False

    # Show dashboard by default
    pages_dict["dashboard"].visible = True

    # Sidebar navigation
    sidebar = ft.Container(
        width=220,
        bgcolor=white,
        border_radius=0,
        padding=ft.padding.symmetric(10, 12),
        content=ft.Column(
            controls=[
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Icon(icons.APARTMENT, size=32, color=primary_color),
                            ft.Text(
                                "Rent Manager",
                                size=16,
                                weight="bold",
                                color=primary_color,
                            ),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=8,
                    ),
                    padding=ft.padding.symmetric(0, 16),
                    margin=ft.margin.only(bottom=24),
                ),
                ft.Divider(height=1),
                create_nav_item(icons.DASHBOARD, "Dashboard", "dashboard"),
                create_nav_item(icons.PERSON, "Owners", "owners"),
                create_nav_item(icons.HOME, "Units", "units"),
                create_nav_item(icons.PEOPLE, "Clients", "clients"),
                create_nav_item(icons.DOMAIN, "Ownerships", "ownerships"),
                create_nav_item(icons.DESCRIPTION, "Assignments", "assignments"),
                create_nav_item(icons.RECEIPT, "Receipts", "receipts"),
                create_nav_item(icons.CALCULATE, "Taxes", "taxes"),
                ft.Divider(height=1),
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Icon(icons.INFO, size=16, color="#999"),
                            ft.Text(
                                "Version 1.0",
                                size=11,
                                color="#999",
                            ),
                        ],
                        spacing=8,
                    ),
                    padding=ft.padding.symmetric(10, 8),
                ),
            ],
            spacing=8,
            scroll=ft.ScrollMode.AUTO,
        ),
    )

    # Main content area
    main_content = ft.Container(
        expand=True,
        bgcolor=light_bg,
        padding=24,
        content=ft.Column(
            controls=[pages_dict[key] for key in pages_dict],
            spacing=0,
            scroll=ft.ScrollMode.AUTO,
        ),
    )

    # Main layout
    main_layout = ft.Row(
        controls=[sidebar, main_content],
        spacing=0,
        expand=True,
    )

    page.add(main_layout)


if __name__ == "__main__":
    ft.app(target=main)