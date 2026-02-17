# 🏘️ Rent Manager - Professional GUI Application

**A modern, intuitive desktop application for managing rental properties, owners, tenants, and tax documentation.**

![Python](https://img.shields.io/badge/Python-3.8+-blue?logo=python)
![Framework](https://img.shields.io/badge/Framework-Flet-blue)
![Status](https://img.shields.io/badge/Status-Production%20Ready-green)
![License](https://img.shields.io/badge/License-MIT-green)

## ✨ Features

### 8 Complete Management Modules

- **📊 Dashboard**: Real-time statistics and recent activity overview
- **👥 Owners**: Manage property owners and their details
- **🏠 Units**: Organize and track rental properties
- **👤 Clients**: Register tenants and business clients
- **🔗 Ownerships**: Configure property ownership shares (fixed or alternating)
- **📋 Assignments**: Create and manage rental contracts
- **💳 Receipts**: Track payments and automatic owner distribution
- **📈 Taxes**: Generate income reports and export data

### Professional Features

✅ Intuitive sidebar navigation  
✅ Material Design 3 aesthetic  
✅ Real-time data tables  
✅ Form validation & error handling  
✅ Success/error notifications  
✅ Confirmation dialogs  
✅ Export to CSV  
✅ SQLite database persistence  

## 🚀 Quick Start

### Installation

1. **Install Python 3.8 or higher** (if not already installed)

2. **Install Flet framework**:
   ```bash
   pip install flet
   ```

### Running the Application

```bash
cd /path/to/rentax
python3 run_gui.py
```

Or directly:
```bash
python3 app.py
```

## 📖 Documentation

### Getting Started Guides
- **[GUI_README.md](GUI_README.md)** - Architecture and technical overview
- **[GUI_PAGES_REFERENCE.md](GUI_PAGES_REFERENCE.md)** - Complete page-by-page guide
- **[IMPLEMENTATION_COMPLETE.md](IMPLEMENTATION_COMPLETE.md)** - Implementation status and statistics

### Quick Tips
- **Add Owner**: Dashboard → Owners → "Add Owner" button
- **Create Unit**: Dashboard → Units → "Add Unit" button
- **Manage Payments**: Dashboard → Receipts → Record payments
- **Generate Report**: Dashboard → Taxes → Select filters and generate

## 🏗️ Application Structure

```
rentax/
├── app.py                      # Main GUI application
├── run_gui.py                  # Launcher script
├── gui/                        # GUI components
│   ├── pages/                  # 8 page implementations
│   │   ├── dashboard_page.py   # Statistics & overview
│   │   ├── owners_page.py      # Owner management
│   │   ├── units_page.py       # Property management
│   │   ├── clients_page.py     # Client management
│   │   ├── ownerships_page.py  # Ownership configuration
│   │   ├── assignments_page.py # Contract management
│   │   ├── receipts_page.py    # Payment tracking
│   │   └── taxes_page.py       # Tax reporting
│   └── components/
│       └── common.py           # 12+ reusable UI components
├── services/                   # Business logic (preserved)
├── models/                     # Data structures (preserved)
├── database.py                 # SQLite persistence (preserved)
└── config.py                   # Configuration (preserved)
```

## 🎨 User Interface

### Navigation
- **Sidebar**: 8 main menu items for easy navigation
- **Header**: Page title and description on each page
- **Content Area**: Dynamic content based on selected page

### Data Entry
- **Add Forms**: Collapsible forms for creating new records
- **Edit**: Inline edit via row actions
- **Delete**: With confirmation dialogs
- **Validation**: Required fields and format checking

### Feedback
- **Success Messages**: Green snackbars confirm actions
- **Error Messages**: Red snackbars show problems
- **Loading States**: Spinners during data operations

## 📊 Core Concepts

### Ownership Models

#### Fixed Ownership
```
Unit "APT-101" owned:
- Alice (50%)
- Bob (50%)

Monthly rent: $2,000
Distribution:
- Alice: $1,000
- Bob: $1,000
```

#### Alternating Ownership
```
Unit "BEACH-VILLA":
- Alice owns odd months (Jan, Mar, May...)
- Bob owns even months (Feb, Apr, Jun...)

Each owner receives 100% of rent in their months
```

### Payment Flow
```
1. Client pays rent
   ↓
2. Record receipt with amount
   ↓
3. System distributes to owners
   ↓
4. Tax reports aggregate by owner/period
```

## 📋 Typical Workflows

### Scenario 1: Add New Rental Property

1. **Create Unit**
   - Reference: "APT-205"
   - City: "Downtown"
   - Type: "2 Bedroom"

2. **Add Owner**
   - Name: "Alice Smith"
   - Legal ID: "123-45-6789"

3. **Configure Ownership**
   - Unit: APT-205
   - Owner: Alice Smith
   - Share: 100%

4. **Create Assignment (Lease)**
   - Unit: APT-205
   - Client: "John Tenant"
   - Rent: $1,500/month
   - Start: 2024-01-01

### Scenario 2: Record Payment & Generate Tax Report

1. **Record Receipt**
   - Assignment: APT-205
   - Period: 2024-01-01
   - Amount: $1,500
   - Owner: Alice Smith

2. **Generate Tax Report**
   - Select: Alice Smith
   - Year: 2024
   - View: Monthly breakdown and totals

3. **Export Report**
   - Click: "Export to CSV"
   - Use in accounting software

## 🔧 System Requirements

- **Python**: 3.8 or higher
- **OS**: Linux, Windows, or macOS
- **Database**: SQLite (included)
- **Memory**: 100 MB (minimum)
- **Disk**: 50 MB (project + data)

## 📱 Platform Support

- ✅ Linux (tested)
- ✅ Windows (via Flet)
- ✅ macOS (via Flet)

## 🎯 Key Features Explained

### Dashboard
- Shows key metrics at a glance
- Displays 4 main statistics
- Recent receipts preview
- Quick access to all modules

### Owners Management
- Add/Edit/Delete owners
- Track phone numbers
- Store legal ID
- Family member count

### Property Management
- Organize units
- Set property types
- Track locations
- Manage addresses

### Client Tracking
- Register tenants (PP) or companies (PM)
- Store contact details
- Track legal IDs
- Manage client relationships

### Ownership Configuration
- Set ownership percentages
- Support multiple owners per unit
- Configure seasonal/alternating ownership
- Handle odd/even month distributions

### Contract Management
- Create rental contracts
- Set rental rates
- Track lease periods
- Apply tax flags (RAS-IR)

### Payment Tracking
- Record monthly payments
- Automatic owner distribution
- Period tracking
- Payment date recording

### Tax Reporting
- Filter by owner
- Filter by year or date range
- View monthly breakdown
- Export to CSV

## 🐛 Troubleshooting

### Application Won't Start

**Error**: "ModuleNotFoundError: No module named 'flet'"
```bash
# Solution: Install Flet
pip install flet
```

**Error**: "Cannot find database"
```bash
# Solution: Ensure you're in the correct directory
cd /path/to/rentax
python3 run_gui.py
```

### Form Won't Submit

- Check all required fields are filled (marked with *)
- Verify date formats: use YYYY-MM-DD
- Check percentage values (0-100)
- Look for error message in red snackbar

### Data Not Showing

- Click refresh or navigate away and back
- Check database file permissions
- Verify records were created (check success message)

## 📞 Support

### Getting Help
1. Check [GUI_PAGES_REFERENCE.md](GUI_PAGES_REFERENCE.md) for detailed guides
2. Review [GUI_README.md](GUI_README.md) for architecture
3. Read inline code comments in page files
4. Examine example workflows in documentation

### Common Questions

**Q: How do I add an owner?**  
A: Click Owners menu → "Add Owner" button → Fill form → Save

**Q: How do I track payments for multiple owners?**  
A: Create one receipt per owner per payment with their ownership share

**Q: How do I generate a tax report?**  
A: Go to Taxes page → Select filters → Click "Generate Report"

**Q: Can I have seasonal rentals?**  
A: Yes! Use Ownerships with "Alternating Ownership" option

## 🔐 Security Notes

- All data stored locally in SQLite database
- No internet connection required
- No data sent to external services
- Database file can be backed up manually

## 📈 Performance

- Fast page switching: <100ms
- Responsive forms
- Efficient data queries
- Minimal memory usage

## 🎓 Learning

### For Users
- See [GUI_PAGES_REFERENCE.md](GUI_PAGES_REFERENCE.md) for detailed instructions
- Follow example workflows for common tasks

### For Developers
- See [GUI_README.md](GUI_README.md) for architecture
- Review component library in `gui/components/common.py`
- Examine service layer in `services/` folder

## 📝 License

MIT License - Feel free to use and modify

## 🙏 Credits

Built with:
- **Flet**: Flutter for Python
- **SQLite3**: Data persistence
- **Material Design 3**: UI framework

## 📜 Version

**Current Version**: 1.0  
**Status**: Production Ready  
**Last Updated**: 2024

---

## 🎬 Get Started Now!

```bash
python3 run_gui.py
```

Then explore the 8 powerful modules to manage your rental properties!

---

**Questions?** See [GUI_PAGES_REFERENCE.md](GUI_PAGES_REFERENCE.md) or [GUI_README.md](GUI_README.md)

**Happy managing!** 🎉
