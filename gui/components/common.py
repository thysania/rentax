import flet as ft
from flet import icons


def create_header(title: str, subtitle: str = ""):
    """Create a page header"""
    return ft.Column(
        controls=[
            ft.Text(title, size=28, weight="bold", color="#2E86AB"),
            ft.Text(subtitle, size=14, color="#666") if subtitle else None,
        ],
        spacing=4,
        margin=ft.margin.only(bottom=20),
    )


def create_data_table(headers: list, rows: list, on_row_click=None):
    """Create a styled data table"""
    columns = [ft.DataColumn(ft.Text(h, weight="w500")) for h in headers]
    
    data_rows = []
    for idx, row in enumerate(rows):
        cells = [ft.DataCell(ft.Text(str(cell))) for cell in row]
        data_rows.append(ft.DataRow(cells=cells, on_select=lambda e, i=idx: on_row_click(i, row) if on_row_click else None))
    
    return ft.DataTable(
        columns=columns,
        rows=data_rows,
        border=ft.border.all(1, "#E0E0E0"),
        border_radius=8,
    )


def create_button(text: str, icon: str, on_click, primary: bool = True):
    """Create a styled button"""
    return ft.ElevatedButton(
        text=text,
        icon=icon,
        on_click=on_click,
        style=ft.ButtonStyle(
            bgcolor="#2E86AB" if primary else "#F0F0F0",
            color="white" if primary else "#333",
            shape=ft.RoundedRectangleBorder(radius=6),
        ),
    )


def create_text_field(label: str, hint: str = "", value: str = "", multiline: bool = False):
    """Create a styled text field"""
    return ft.TextField(
        label=label,
        hint_text=hint,
        value=value,
        multiline=multiline,
        min_lines=1 if not multiline else 3,
        border_radius=6,
        border="underline",
    )


def create_stat_card(title: str, value: str, icon: str, color: str = "#2E86AB"):
    """Create a statistics card"""
    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.Icon(icon, size=28, color=color),
                        ft.Text(title, size=12, color="#666", weight="w500"),
                    ],
                    spacing=12,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                ft.Text(value, size=24, weight="bold", color="#333"),
            ],
            spacing=8,
        ),
        bgcolor="white",
        padding=16,
        border_radius=8,
        border=ft.border.all(1, "#E0E0E0"),
        shadow=ft.BoxShadow(blur_radius=2, spread_radius=1, color="#0000000A"),
    )


def create_alert_dialog(title: str, content: str, on_confirm, on_cancel=None, is_error: bool = False):
    """Create an alert dialog"""
    def handle_confirm(e):
        on_confirm()

    def handle_cancel(e):
        if on_cancel:
            on_cancel()

    dlg = ft.AlertDialog(
        title=ft.Text(title, weight="bold"),
        content=ft.Text(content),
        actions=[
            ft.TextButton("Cancel", on_click=handle_cancel) if on_cancel else None,
            ft.ElevatedButton(
                "Confirm",
                on_click=handle_confirm,
                style=ft.ButtonStyle(
                    bgcolor="#2E86AB",
                    color="white",
                ),
            ),
        ],
    )
    return dlg


def create_snackbar(message: str, is_error: bool = False):
    """Create a snackbar notification"""
    return ft.SnackBar(
        ft.Text(message),
        bgcolor="#4CAF50" if not is_error else "#F44336",
    )


def create_form_field_row(label: str, control: ft.Control):
    """Create a form field row with label"""
    return ft.Row(
        controls=[
            ft.Container(
                content=ft.Text(label, size=13, weight="w500", color="#333"),
                width=150,
            ),
            ft.Container(expand=True, content=control),
        ],
        spacing=12,
        vertical_alignment=ft.CrossAxisAlignment.START,
        height=60,
    )


def create_loading_spinner():
    """Create a loading spinner"""
    return ft.ProgressRing(
        width=40,
        height=40,
        stroke_width=4,
        stroke_width_border=2,
    )
