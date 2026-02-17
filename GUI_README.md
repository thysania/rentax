# Rent Manager - GUI Application

## Overview

Rent Manager is now a modern, minimalist GUI application built with **Flet** (Flutter for Python). It provides an intuitive interface for managing rental properties, owners, tenants, contracts, receipts, and tax calculations.

## Features

### 🏠 Dashboard
- Quick statistics: Total owners, units, clients, and active assignments
- Recent receipts preview
- Quick access to key metrics

### 👤 Owners Management
- Add, edit, and delete property owners
- Track phone numbers, legal IDs, and family counts
- View all owners in a formatted table

### 🏢 Units Management
- Manage rental units with details like location, floor, and unit type
- Add, edit, and delete units
- Organize by city and neighborhood

### 👥 Clients Management
- Add and manage tenants and business clients
- Track client type (person or company)
- Manage contact information and legal IDs

### 🔗 Ownerships Management
- Define ownership shares for units
- Support shared and alternating ownership
- Manage complex ownership arrangements

### 📋 Assignments Management
- Create rental contracts linking units, owners, and clients
- Define rent amounts and payment schedules
- Track alternating ownership periods
- Manage RAS IR tax flags

### 🧾 Receipts Management
- Generate receipts for entire months (batch processing)
- Record actual payments received
- Track receipt logs and payment history
- Export receipt data in multiple formats (detailed, by-owner, minimal)

### 💰 Taxes Management
- Calculate taxes based on received payments
- Apply family deductions and tax rates
- Export tax reports in CSV format
- Support multiple tax calculation formats

## UI Design

The application features a clean, minimalist design with:

- **Left Sidebar**: Easy navigation with color-coded icons
- **Professional Color Scheme**:
  - Primary: Professional blue (#2E86AB)
  - Secondary: Purple accent (#A23B72)
  - Light backgrounds for reduced eye strain
  
- **Intuitive Components**:
  - Data tables with inline actions (Edit, Delete)
  - Modal forms for adding/editing records
  - Snap notifications for success/error messages
  - Material Design 3 compliance

## Installation

### Prerequisites
- Python 3.8 or higher
- Flet framework
- SQLite3

### Setup

```bash
# Install dependencies
pip install flet

# Navigate to the application directory
cd /home/osama/rentax

# Run the application
python3 app.py
```

## File Structure

```
rentax/
├── app.py                           # Main Flet application entry point
├── gui/
│   ├── __init__.py
│   ├── components/
│   │   ├── __init__.py
│   │   └── common.py               # Reusable UI components
│   └── pages/
│       ├── __init__.py
│       ├── dashboard_page.py       # Dashboard page
│       ├── owners_page.py          # Owners management
│       ├── units_page.py           # Units management
│       ├── clients_page.py         # Clients management
│       ├── ownerships_page.py      # Ownerships management
│       ├── assignments_page.py     # Assignments management
│       ├── receipts_page.py        # Receipts management
│       └── taxes_page.py           # Taxes reporting
├── services/                        # Business logic (unchanged)
├── models/                          # Data models (unchanged)
├── sql/                            # Database schema (unchanged)
└── database.py                      # Database initialization (unchanged)
```

## Key Components

### Common UI Components (`gui/components/common.py`)

- `create_header()` - Page header with title and subtitle
- `create_data_table()` - Styled data tables
- `create_button()` - Styled buttons
- `create_text_field()` - Input fields
- `create_stat_card()` - Statistics display cards
- `create_form_field_row()` - Labeled form fields
- `create_alert_dialog()` - Confirmation dialogs
- `create_snackbar()` - Notification messages

### Page Implementation Pattern

Each page in `gui/pages/` follows this pattern:

```python
import flet as ft
from gui.components.common import create_header
from services import relevant_service

def create(page: ft.Page):
    """Create page content"""
    
    def load_data():
        # Load data from service
        pass
    
    def add_item(e):
        # Add new item logic
        pass
    
    def edit_item(item):
        # Edit item logic
        pass
    
    def delete_item(item):
        # Delete item logic
        pass
    
    content = ft.Column(
        controls=[
            create_header("Title", "Subtitle"),
            # Add your controls
        ],
        spacing=16,
        scroll=ft.ScrollMode.AUTO,
    )
    
    return content
```

## Usage Examples

### Adding an Owner

1. Navigate to **Owners** in the sidebar
2. Click **Add Owner** button
3. Fill in the form fields:
   - Owner Name (required)
   - Phone (optional)
   - Legal ID (optional)
   - Family Count (optional)
4. Click **Save**
5. Success notification appears

### Managing Units

1. Navigate to **Units** in the sidebar
2. Click **Add Unit** to create new units
3. View all units in the table
4. Use **Edit** icon to modify unit details
5. Use **Delete** icon to remove units

### Generating Receipts

1. Navigate to **Receipts**
2. Select the month for batch generation
3. Set the issue date
4. System generates receipts for all active assignments

## Database Integration

The GUI seamlessly integrates with the existing SQLite database:

- Database initialization happens automatically on app startup
- All services maintain their original function-based structure
- Data persistence is guaranteed through the existing schema

## Navigation

- **Sidebar**: Click any menu item to navigate
- **Active Page**: Only one page is visible at a time
- **Responsive**: Adapts to window resizing

## Error Handling

All pages include:
- Validation for required fields
- Error notifications with helpful messages
- Confirmation dialogs for destructive actions
- Graceful error recovery

## Status

✅ **Completed**:
- Dashboard with statistics
- Owners management
- Units management
- Navigation system
- Common components library
- Error handling and notifications

🚀 **Ready for Enhancement**:
- Clients management (placeholder)
- Ownerships management (placeholder)
- Assignments management (placeholder)
- Receipts management (placeholder)
- Taxes reporting (placeholder)

## Future Enhancements

Planned features:
- Real-time data synchronization
- Dark mode support
- Print/export capabilities
- Advanced filtering and search
- Data backup and restore
- User authentication
- Multi-user support
- Audit logging

## Support

For issues or questions, refer to the project documentation in `README.md`.

## License

Same as the parent project.

---

**Version**: 1.0  
**Last Updated**: February 15, 2026  
**Technology**: Flet (Flutter for Python) + SQLite3
