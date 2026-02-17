# GUI Pages Reference Guide

Complete documentation for all Rent Manager GUI pages and features.

## Table of Contents

- [Dashboard](#dashboard)
- [Owners](#owners)
- [Units](#units)
- [Clients](#clients)
- [Ownerships](#ownerships)
- [Assignments](#assignments)
- [Receipts](#receipts)
- [Taxes](#taxes)

---

## Dashboard

**File**: `gui/pages/dashboard_page.py`

The Dashboard is the main landing page displaying key metrics and recent activity at a glance.

### Features

- **Statistics Cards**: Four main stat cards showing:
  - Total Owners
  - Total Units
  - Total Clients
  - Total Assignments

- **Recent Receipts Table**: Shows the 10 most recent payment receipts with:
  - Owner name
  - Assignment ID
  - Period (month)
  - Amount paid
  - Payment date

### Data Sources

- Owner count from `owner_service.list_all_owners()`
- Unit count from `unit_service.list_all_units()`
- Client count from `client_service.list_all_clients()`
- Assignment count from `assignment_service.list_all_assignments()`
- Receipt list from `receipt_service.list_all_receipts()`

### Example Use

1. Launch the application
2. Dashboard displays automatically
3. Click any other menu item to navigate
4. Return to Dashboard via sidebar

---

## Owners

**File**: `gui/pages/owners_page.py`

Manage rental property owners and their information.

### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| Name | Text | ✓ | Owner's full name |
| Phone | Text | | Phone number |
| Legal ID | Text | | Tax ID or national ID |
| Family Count | Number | | Number of family members |

### Operations

#### Add Owner
1. Click "Add Owner" button
2. Fill required field (Name)
3. Optionally add Phone, Legal ID, Family Count
4. Click "Save"
5. Success notification appears
6. Form clears and new owner appears in table

#### Edit Owner
1. Click edit icon (✏️) in table row
2. Form populates with current values
3. Modify fields as needed
4. Click "Save"
5. Changes are applied immediately

#### Delete Owner
1. Click delete icon (🗑️) in table row
2. Confirmation dialog appears
3. Confirm deletion
4. Owner is removed from system

### Validation

- **Name**: Required field, cannot be empty
- **Phone**: Optional, any format accepted
- **Legal ID**: Optional, unique per owner
- **Family Count**: Optional, must be numeric

### Example Workflow

```
1. Add three owners:
   - John Smith (Phone: 555-0101)
   - Maria Garcia (Legal ID: 123-45-6789)
   - James Brown (Family Count: 4)

2. Edit John Smith's phone to 555-0102

3. Delete James Brown when property is sold
```

---

## Units

**File**: `gui/pages/units_page.py`

Manage rental properties (units/apartments).

### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| Reference | Text | ✓ | Unit identifier (e.g., "APT-101") |
| City | Text | | City location |
| Neighborhood | Text | | Neighborhood name |
| Floor | Number | | Floor number |
| Unit Type | Dropdown | | Type: Studio, 1BR, 2BR, 3BR, 4BR+, Commercial |

### Operations

#### Add Unit
1. Click "Add Unit" button
2. Enter unique Reference (e.g., "APT-202")
3. Add optional location details (City, Neighborhood)
4. Set Floor number
5. Select Unit Type
6. Click "Save"

#### Edit Unit
1. Click edit icon (✏️)
2. Modify any field
3. Click "Save"

#### Delete Unit
1. Click delete icon (🗑️)
2. Confirm in dialog
3. Unit is removed

### Unit Types

Available unit types for classification:
- Studio
- 1 Bedroom (1BR)
- 2 Bedrooms (2BR)
- 3 Bedrooms (3BR)
- 4+ Bedrooms (4BR+)
- Commercial

### Constraints

- Reference must be unique
- Can only delete if no active assignments
- Ownership can be added separately

### Example Workflow

```
1. Add units:
   - APT-101 in Downtown, Floor 1, 1BR
   - APT-202 in Midtown, Floor 2, 2BR
   - SHOP-001 in Downtown, Floor 0, Commercial

2. Organize by floor or type in the list

3. Edit APT-101 neighborhood to "Financial District"

4. View all 3+ bedroom units for high-value rentals
```

---

## Clients

**File**: `gui/pages/clients_page.py`

Manage tenants and business clients renting units.

### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| Name | Text | ✓ | Client/tenant name |
| Phone | Text | | Contact phone number |
| Legal ID | Text | | Tax ID for businesses or ID for persons |
| Client Type | Dropdown | ✓ | PP (Person) or PM (Company) |

### Client Types

- **PP (Person)**: Individual tenant
- **PM (Company/Business)**: Corporate or business entity

### Operations

#### Add Client
1. Click "Add Client" button
2. Enter Name (required)
3. Enter Phone (optional)
4. Enter Legal ID (optional)
5. Select Client Type (Person or Company)
6. Click "Save"

#### Edit Client
1. Click edit icon (✏️)
2. Modify fields (except ID is auto-generated)
3. Click "Save"

#### Delete Client
1. Click delete icon (🗑️)
2. Confirm deletion
3. Client removed

### Validation

- **Name**: Required, cannot be empty
- **Client Type**: Required, must select PP or PM
- **Phone/Legal ID**: Optional, any format

### Example Workflow

```
1. Add clients:
   - Alice Johnson (PP) - Phone: 555-1234
   - Tech Corp (PM) - Legal ID: 98-7654321
   - Bob Smith (PP) - Legal ID: 123-45-6789

2. Track which are individuals vs companies

3. Edit Alice's phone when she calls with update

4. Delete client record when they move away
```

### Tax Considerations

- Client type (PP/PM) affects tax reporting
- **RAS-IR tax flag** is set per assignment, not per client
- Same client can have multiple assignments to different units

---

## Ownerships

**File**: `gui/pages/ownerships_page.py`

Manage ownership shares of units between multiple owners.

### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| Unit | Dropdown | ✓ | Select which unit |
| Owner | Dropdown | ✓ | Select which owner |
| Share % | Number | ✓ | Ownership percentage (0-100) |
| Alternating Ownership | Checkbox | | Enable seasonal/monthly splits |
| Odd/Even Months | Dropdown | | If alternating: odd (1,3,5...) or even (2,4,6...) |

### Ownership Types

#### Fixed Share
- Owner holds same percentage year-round
- Example: Unit owned 60% by John, 40% by Maria

#### Alternating (Seasonal)
- Owner's share changes monthly
- **Odd months**: Owner 1 owns in Jan, Mar, May, Jul, Sep, Nov
- **Even months**: Owner 2 owns in Feb, Apr, Jun, Aug, Oct, Dec
- Used for seasonal properties or shared vacation homes

### Operations

#### Add Ownership
1. Click "Add Ownership" button
2. Select Unit from dropdown
3. Select Owner from dropdown
4. Enter Share % (1-100)
5. (Optional) Check "Alternating Ownership"
6. If alternating, select Odd or Even months
7. Click "Save"

#### Edit Ownership
1. Click edit icon (✏️)
2. Modify Unit, Owner, or Share %
3. Toggle alternating if needed
4. Click "Save"

#### Delete Ownership
1. Click delete icon (🗑️)
2. Confirm deletion
3. Ownership removed

### Validation

- **Share %**: Must be 0-100
- **Unit/Owner**: Both required
- **Total ownership per unit**: Should not exceed 100% (if not fully leased)

### Constraints

- Each unit must have at least one owner
- Multiple owners can share a unit
- Ownerships must sum correctly for payment distribution

### Example Workflows

#### Scenario 1: Shared Ownership
```
APT-101:
- Owner: John Smith, Share: 50%
- Owner: Maria Garcia, Share: 50%

When $1000 rent collected:
- John receives: $500
- Maria receives: $500
```

#### Scenario 2: Alternating Seasonal Ownership
```
BEACH-VILLA:
- Owner: Alice (Odd months), Share: 100%
- Owner: Bob (Even months), Share: 100%

Jan rent: All to Alice
Feb rent: All to Bob
Mar rent: All to Alice
... continues alternating
```

#### Scenario 3: Mixed Partial Ownership
```
CONDO-201:
- Owner: Corp Holdings, Share: 70%
- Owner: John Smith, Share: 30%

$2000 rent:
- Corp Holdings: $1400
- John Smith: $600
```

---

## Assignments

**File**: `gui/pages/assignments_page.py`

Manage rental contracts (who rents which unit and for how long).

### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| Unit | Dropdown | ✓ | Which unit is being rented |
| Client | Dropdown | ✓ | Who is renting (tenant) |
| Start Date | Date | ✓ | Rental start date (YYYY-MM-DD) |
| End Date | Date | | Rental end date (YYYY-MM-DD) - leave empty for ongoing |
| Monthly Rent Amount | Currency | ✓ | Fixed monthly rent |
| RAS-IR Tax | Checkbox | | Apply rental tax withholding |

### Operations

#### Add Assignment
1. Click "Add Assignment" button
2. Select Unit from dropdown
3. Select Client (tenant) from dropdown
4. Enter Start Date (YYYY-MM-DD format)
5. Enter End Date (optional - leave empty for ongoing lease)
6. Enter Monthly Rent Amount (e.g., 1500)
7. (Optional) Check "RAS-IR Tax" if applicable
8. Click "Save"

#### Edit Assignment
1. Click edit icon (✏️)
2. Modify any field
3. Click "Save"

#### Delete Assignment
1. Click delete icon (🗑️)
2. Confirm deletion
3. Assignment removed

### Date Format

Use **YYYY-MM-DD** format:
- January 15, 2024 → `2024-01-15`
- December 31, 2024 → `2024-12-31`

### RAS-IR Tax Flag

**RAS-IR** is an Italian rental tax withholding requirement:
- Check this box if rent is subject to withholding
- Affects tax calculations for the owner
- Independent of client type (PP/PM)

### Constraints

- One unit can only have one active assignment at a time
- Cannot overlap with existing assignments
- Rent amount is locked (doesn't change per month)
- Units cannot be vacant and rented simultaneously

### Example Workflow

```
1. Create assignment:
   - Unit: APT-102
   - Client: Alice Johnson (tenant)
   - Period: 2024-01-01 to 2024-12-31
   - Rent: $1200/month
   - RAS-IR: Yes

2. Receive January payment → create receipt
   Amount: $1200 → distributed to unit owners per ownership shares

3. When year-end report runs:
   - Tallies 12 months of receipts
   - Marks as RAS-IR income for tax purposes
```

---

## Receipts

**File**: `gui/pages/receipts_page.py`

Record and track rent payments received from tenants.

### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| Assignment | Dropdown | ✓ | Which rental contract this payment applies to |
| Owner | Dropdown | ✓ | Which owner receives this portion |
| Period | Date | ✓ | Month of rent paid (YYYY-MM-01) |
| Payment Date | Date | ✓ | Date payment was received (YYYY-MM-DD) |
| Amount | Currency | ✓ | Payment amount in local currency |

### Receipt Flow

1. **Client pays rent** → 2. **Create receipt** → 3. **Amount distributed to owners** based on ownership shares

### Operations

#### Add Receipt
1. Click "Add Receipt" button
2. Select Assignment (which tenant's payment)
3. Select Owner (who receives this payment)
4. Enter Period (month of rent, e.g., `2024-01-01`)
5. Enter Payment Date (when check cleared, e.g., `2024-01-10`)
6. Enter Amount paid
7. Click "Save"

#### Edit Receipt
1. Click edit icon (✏️)
2. Modify fields
3. Click "Save"

#### Delete Receipt
1. Click delete icon (🗑️)
2. Confirm deletion
3. Receipt removed (reverses owner's income)

### Payment Distribution Example

**Scenario**: Unit APT-201 owned 60% by John, 40% by Maria

```
Tenant pays $1000 for January rent:

Receipt #1:
- Assignment: APT-201
- Owner: John (60% owner)
- Period: 2024-01-01
- Payment Date: 2024-01-05
- Amount: $600  ← John's share (60% of $1000)

Receipt #2:
- Assignment: APT-201
- Owner: Maria (40% owner)
- Period: 2024-01-01
- Payment Date: 2024-01-05
- Amount: $400  ← Maria's share (40% of $1000)
```

### Date Format Rules

- **Period**: `YYYY-MM-01` (always the 1st of the month)
  - January 2024 → `2024-01-01`
  - February 2024 → `2024-02-01`

- **Payment Date**: `YYYY-MM-DD` (actual date received)
  - January 5, 2024 → `2024-01-05`

### Data Validation

- Assignment must exist
- Owner must be a valid owner of the assigned unit
- Amount must be positive
- Period must be valid date
- Payment date must be valid date

---

## Taxes

**File**: `gui/pages/taxes_page.py`

Generate tax reports and calculate rental income summaries.

### Report Parameters

#### Filter By Owner
- Select single owner from dropdown
- Shows all rental income for that owner
- Useful for individual tax filing

#### Filter By Year
- Enter year (e.g., 2024)
- Aggregates all receipts from January 1 - December 31
- Quick yearly summary

#### Filter By Date Range
- Start Date and End Date (YYYY-MM-DD)
- Custom period reporting
- Useful for quarterly reports or interim periods

### Report Output

The tax report displays:

1. **Owner Information**
   - Name
   - Legal ID
   - Phone

2. **Summary Cards**
   - **Total Receipts**: Sum of all payments in period
   - **Rental Income**: Total rent income (before tax)
   - **RAS-IR Count**: Number of months with RAS-IR withholding

3. **Monthly Breakdown Table**
   - Month (e.g., "January 2024")
   - Receipt count for that month
   - Total amount received
   - RAS-IR flag (Yes/No)

4. **Export Options**
   - Export to CSV: Download data for spreadsheet/accounting software
   - Print Report: Generate printable PDF/page view

### Example Reports

#### Annual Ownership Report for Alice
```
Owner: Alice Smith
Legal ID: 123-45-6789

Tax Year: 2024

Summary:
- Total Receipts: $12,450
- Rental Income: $12,450
- RAS-IR Count: 3 months

Monthly Breakdown:
January 2024: 4 receipts, $4,000, RAS-IR: Yes
February 2024: 3 receipts, $3,450, RAS-IR: No
March 2024: 2 receipts, $2,450, RAS-IR: Yes
... (rest of year)
```

#### Quarterly Report (Jan-Mar 2024)
```
Period: January 1, 2024 to March 31, 2024

Summary:
- Total Receipts: $9,900
- Rental Income: $9,900
- RAS-IR Count: 2 months
```

### Operations

#### Generate Report
1. (Optional) Select Owner from dropdown
2. (Optional) Enter Year OR Start/End dates
3. Click "Generate Report" button
4. Report displays with all calculations

#### Export Report
1. After generating report
2. Click "Export to CSV" button
3. Data saved to file for accounting software

#### Print Report
1. After generating report
2. Click "Print Report" button
3. Formatted page opens for printing/PDF save

### Tax Compliance Features

- **RAS-IR Tracking**: Identifies months subject to withholding
- **Income Aggregation**: Totals income per owner per period
- **Multi-owner Units**: Correctly attributes shares to each owner
- **Date Range Flexibility**: Reports for any calendar period

### Data Sources

Reports aggregate from:
- `receipt_service`: All payment records
- `assignment_service`: Rental contract details
- `owner_service`: Owner information
- `unit_service`: Property information

---

## Common UI Patterns

### Data Tables

All CRUD pages use similar data table patterns:

| Column | Content |
|--------|---------|
| ID | Auto-generated record ID |
| Key Info | Name, reference, or primary identifier |
| Status/Type | Category or status info |
| Additional | Other relevant fields |
| Actions | Edit (✏️) and Delete (🗑️) buttons |

### Forms

Standard form patterns across all pages:

1. **Add Button**: Opens collapsible form
2. **Form Fields**: Text inputs, dropdowns, checkboxes
3. **Validation**: Error messages for required fields
4. **Save/Cancel**: Action buttons
5. **Success Message**: Snackbar notification after save

### Dialogs

Confirmation dialogs for destructive actions:
- Delete operations require explicit confirmation
- Shows what will be deleted
- Cancel or Confirm buttons

### Notifications

Two types of feedback messages:

- **Success** (Green): Operation completed successfully
- **Error** (Red): Problem occurred, action failed

---

## Keyboard Shortcuts (Coming Soon)

Future enhancements may include:
- `Ctrl+N`: New record
- `Ctrl+S`: Save
- `Ctrl+Q`: Quit
- `Tab`: Navigate between fields
- `Enter`: Submit form

---

## Troubleshooting

### Import Errors

If you see "ModuleNotFoundError", verify:
1. All Python files are in correct directories
2. `__init__.py` files exist in all package directories
3. Service modules are in `services/` folder

### Database Errors

If receipts won't save:
1. Verify database.db exists in project root
2. Check ownership records exist for selected unit
3. Ensure assignment record exists

### Date Parsing Errors

Use correct format: **YYYY-MM-DD**
- ✓ Correct: `2024-01-15`
- ✗ Wrong: `01/15/2024` or `Jan 15, 2024`

---

## Related Documentation

- [GUI_README.md](GUI_README.md): Architecture and setup guide
- [Copilot Instructions](/.github/copilot-instructions.md): Domain architecture
- Service layer: `services/` - Business logic implementations
- Database: `database.py`, `sql/schema.sql` - Data persistence

---

**Last Updated**: 2024
**Version**: 1.0
**Status**: Complete - All 8 pages fully functional
