Rentax — Rental management CLI

Overview

Rentax is a CLI-based rental property management system. It supports owners, units, clients, assignments (contracts), receipts, payments and tax computation/export features.

Taxes CSV export (examples)

The taxes CLI can compute owner taxes for a given year and export CSV reports in three formats:

- detailed: One line per owner with full columns (gross, abattement amount, tax after bracket/deduction, family deduction, final tax unrounded, rounded tax, RAS withheld, due tax)
- by-assignment: One line per assignment/receipt (unit reference, city, client, assignment id, gross) followed by an owner summary (same columns as detailed)
- minimal: One line per owner (owner_id, owner_name, year, gross_revenue, rounded_tax)

1) Run the CLI and open the Taxes menu:

$ python3 app.py
# then from the main menu choose Taxes

2) Follow the prompts (example for stdout export):

Year (YYYY): 2026
Owner ID (blank = all owners):  [ENTER]
Export CSV report? (y/N): y
Select format:
1. detailed (one owner line)
2. by-assignment (lines per assignment then owner summary)
3. minimal
Choose format [1]: 2
Output file (path) or '-' for stdout [taxes_2026.csv]: -

The CSV will be printed to stdout.

Receipts CSV export (example)

The receipts menu also supports interactive CSV export with the same numeric format choices. Example interaction to print to stdout:

1) Run the CLI and open the Receipts menu
$ python3 app.py
# then choose Receipts

2) Follow the prompts (example printing to stdout):

Year (YYYY): 2026
Owner ID (blank = all owners):  [ENTER]
Select format:
1. detailed (lines per receipt)
2. by-owner (owner aggregation)
3. minimal
Choose format [1]: 1
Output file (path) or '-' for stdout [receipts_2026.csv]: -

The CSV will be printed to stdout.

Example `detailed` header

owner_id,owner_name,owner_legal_id,gross_revenue,abattement_amount,tax_after_rate_minus_deduction,family_deduction,final_tax_unrounded,rounded_tax,ras_withheld,due_tax

Example `by-assignment` first lines

owner_id,owner_name,owner_legal_id,unit_reference,unit_city,client_name,client_legal_id,assignment_id,gross,gross_revenue,abattement_amount,tax_after_rate_minus_deduction,family_deduction,final_tax_unrounded,rounded_tax,ras_withheld,due_tax

(Then a line per assignment followed by a summary line for the owner.)

Example `minimal` header

owner_id,owner_name,year,gross_revenue,rounded_tax

Notes

- CSVs are UTF-8, comma-delimited and include a header row.
- Monetary values are formatted with 2 decimals. The `rounded_tax` column contains the final tax rounded up to the nearest integer (non-negative), as per project policy.

Models folder

The `models/` directory is intended to hold domain model definitions (plain dataclasses or similar) that describe the shape of entities (Owner, Client, Unit, Assignment, Receipt). Currently the files are placeholders but we may introduce small dataclasses and migrate service return values to typed model objects over time to improve validation and clarity.

Contributing

Open issues and PRs are welcome. Run tests with:

$ python3 -m pytest

License

MIT
