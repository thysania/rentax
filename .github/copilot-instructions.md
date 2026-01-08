# Copilot Instructions for Rent Manager

## Project Overview
**Rent Manager** is a CLI-based rental property management system managing a complex domain: owners hold partial/full units, clients rent units via assignments (contracts), and rent payments flow via receipts to owners based on ownership shares. Tax calculations aggregate receipt data per owner.

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

**Domains**: `owner`, `unit`, `client`, `assignment`, `receipt`, `taxes`. Each has vertical: model → service → CLI menu.

### Key Patterns

**Service-Based Logic**: All business logic in `services/`, never in models or CLI. Models are pure data holders.

**CLI Independence**: Each `cli/{domain}_menu.py` imports **only** from corresponding `services/{domain}_service.py`, never directly from models or database.

**Single Database Module**: `database.py` handles SQLite setup and schema initialization. All services access data through passed `db` parameter.

**Configuration**: `config.py` stores DB path, table names, and environment settings—reference, don't hardcode paths.

## Core Workflows

### Domain-Specific Logic

**Ownerships** (Units → Owners): Units belong to owners via `ownerships` table supporting:
  - Shared ownership (`share_percent`, e.g., 50%) for co-owned units
  - Alternating ownership (`is_alternating=1`, `odd_even='odd'`) for temporal splits (owner A months 1-6, owner B months 7-12)
  - Services must enforce: ownership splits must sum to 100% per unit (or < 100% if vacancy exists)

**Assignments** (Contracts): A client rents a unit for a period at fixed `rent_amount`. Multiple sequential assignments allowed; no overlaps.

**Receipts** (Payment Distribution): When a client pays rent for `period` (month), receipt splits payment to unit owners per ownership share. Service must:
  - Verify `ownership_id` owned that unit during `period`
  - Calculate owner share: `amount * ownership.share_percent / 100`
  - Handle alternating splits (e.g., only owner A owns in odd months)

**Client Types**: `PP` (person), `PM` (company); affects tax handling. `ras_ir` flag tracks French tax status.

### Adding a New Domain

1. **Model** (`models/{domain}.py`): Data class with basic field validation
2. **Service** (`services/{domain}_service.py`): CRUD + domain logic (constructor takes `db`)
3. **CLI Menu** (`cli/{domain}_menu.py`): Call service methods, format output for user
4. **Database Schema** (`sql/schema.sql`): Table definitions + FK constraints
5. **Entrypoint** (`app.py`): Import + wire menu into main CLI flow

### Database Initialization
- `database.py` reads `sql/schema.sql` on first run; creates tables if missing
- Enable `PRAGMA foreign_keys = ON` to enforce referential integrity (in schema.sql)
- Services assume tables exist; validate data, not schema
- Relationships: `owners` ← `ownerships` → `units` ← `assignments` → `clients`, `assignments` ← `receipts`

## Code Conventions

**Naming**: 
- Service methods: `create_X()`, `get_X()`, `update_X()`, `delete_X()`, `list_all_X()`
- Models: `from models.owner import Owner`
- Services: `from services.owner_service import OwnerService`
- Table names in schema: lowercase plural (`owners`, `assignments`, `receipts`)
- Date fields in schema: use `DATE` type, ISO 8601 strings in code

**Error Handling**: 
- Services raise exceptions with context (e.g., `ValueError("Owner {id} not found")`)
- CLI catches exceptions and displays user-friendly messages
- Don't silently fail; propagate data errors to service layer

**Dates**: 
- Storage: ISO 8601 format (`YYYY-MM-DD`) in database
- Display: Localized format via `utils/dates.py` utilities
- Receipts track `period` (e.g., `2026-01-01` for January rent) and `created_at` (payment date)

**Foreign Keys**:
- Always specify `FOREIGN KEY (column) REFERENCES table(id)` in schema
- Services validate FK existence before insert (e.g., confirm owner exists before creating unit)

## Integration Points & Constraints

- **Receipts** reference both `assignment_id` (which tenant) and `ownership_id` (which owner) to track payment flow
- **Assignments** lock `rent_amount` at contract start (don't change mid-period)
- **Units** can be vacant (no assignment) but must have ownership defined (at least 1 owner)
- **Ownership Share Math**: For alternating ownership, validate that each unit has > 0% ownership in every period
- **Tax Aggregation**: Taxes sum receipts per owner within date range; filter by owner + period

## Development Workflow

1. **Before implementing**: Check schema.sql to understand table structure
2. **When adding fields**: Update model, service methods, and schema in tandem
3. **For multi-owner logic**: Test both fixed-share (50/50) and alternating (odd/even) scenarios
4. **When debugging receipts**: Trace chain: Receipt → Assignment → Unit → Ownerships → Owner
5. **Testing**: CLI layer is thin; test most logic in services (CRUD, calculations, constraints)

## Quick Reference: Key Files

| File | Purpose |
|------|---------|
| `database.py` | SQLite connection, schema loader, ensure tables exist |
| `config.py` | DB path, table names, environment config |
| `sql/schema.sql` | Table definitions with FK + constraints |
| `models/{domain}.py` | Data class + field validation (no DB calls) |
| `services/{domain}_service.py` | CRUD + business logic (all DB calls here) |
| `cli/{domain}_menu.py` | User prompts/display (calls service methods) |
| `utils/dates.py` | Date parsing/formatting helpers |
| `app.py` | Main entrypoint, CLI menu routing |
