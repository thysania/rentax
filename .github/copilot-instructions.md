# Copilot Instructions for Rent Manager

## Project Overview
**Rent Manager** is a CLI-based rental property management system. It manages owners, rental units, client tenants, assignments (unit-to-client contracts), receipts, and tax calculations.

## Architecture

### Layered Structure
```
CLI Layer        → cli/{*_menu.py}  (user interaction)
        ↓
Service Layer    → services/{*_service.py}  (business logic)
        ↓
Model Layer      → models/{*.py}  (data structures)
        ↓
Data Layer       → database.py  (SQLite persistence)
```

Each domain (Owner, Unit, Client, Assignment, Receipt, Taxes) has its own vertical: model → service → CLI menu.

### Key Patterns

**Service-Based Logic**: Business logic lives in `services/`, never in models or CLI. Models are pure data holders.

**CLI Independence**: Each `cli/{domain}_menu.py` imports from the corresponding `services/{domain}_service.py`, never directly from models or database.

**Single Database Module**: `database.py` contains the SQLite connection setup and schema initialization. All services access data through this.

**Configuration**: `config.py` stores constants (DB path, app settings) that might vary by environment.

## Core Workflows

### Adding a New Domain (e.g., Maintenance)

1. **Model** (`models/maintenance.py`): Define data structure with basic validation
2. **Service** (`services/maintenance_service.py`): CRUD + domain logic (e.g., cost calculations)
3. **CLI Menu** (`cli/maintenance_menu.py`): Call service methods, format output
4. **Database Schema** (`sql/schema.sql`): Add table definition
5. **Entry Point** (`app.py`): Import and wire menu into main CLI

### Database Initialization
- `database.py` reads `sql/schema.sql` on startup if tables don't exist
- Services assume tables exist; no schema validation in services
- Foreign key constraints enforce referential integrity (Owner → Unit → Assignment → Receipt)

## Code Conventions

**Naming**: 
- Service methods: `create_X()`, `get_X()`, `update_X()`, `delete_X()`, `list_all_X()`
- Models: `from models.owner import Owner`
- Services: `from services.owner_service import OwnerService`

**Error Handling**: Services raise exceptions with meaningful messages; CLI catches and formats for user display.

**Dates**: Use `utils/dates.py` utilities for parsing/formatting (ISO 8601 for storage, user-friendly for display).

## Integration Points

- **Receipts** reference Assignments (tracks which tenant paid)
- **Assignments** reference Owner, Unit, and Client
- **Units** reference Owner
- **Taxes** aggregate Receipt data for owner tax calculations

Maintain these relationships when modifying services.

## Getting Started

1. Implement `database.py`: SQLite setup, schema loader, connection manager
2. Implement models with required fields and basic validation
3. Implement services with CRUD operations
4. Implement CLI menus with input/output handling
5. Wire everything in `app.py` as the entry point

## Example Service Pattern
```python
# services/owner_service.py
from models.owner import Owner

class OwnerService:
    def __init__(self, db):
        self.db = db
    
    def create_owner(self, name, email):
        # Insert, return ID
        pass
    
    def get_owner(self, owner_id):
        # Query and return Owner object
        pass
```
