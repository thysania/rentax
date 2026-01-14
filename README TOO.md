
# Core Data Model Concepts

This project **intentionally separates assignments from receipts**.
They are **not the same thing** and must never be merged.

If this distinction is not respected, alternation logic, ownership splits, and tax calculations will break.

---

## 1. Assignment (Ownership Logic)

An **assignment** represents the **contractual ownership reality** of a unit.

It answers:

> Who owns which unit, in what proportion, and under what alternation rules?

Assignments are:

* Long-term
* Rarely modified
* The **source of truth** for ownership and entitlement

### Key characteristics

* Links **unit ↔ owner**
* Defines **ownership share** (percentage or alternation)
* Defines **how rent entitlement changes over time**
* Does **not** represent money received

### Example

Unit U001:

* Owner A: 50%
* Owner B: 50%
* Alternation: monthly (Jan A, Feb B, Mar A...)

This is an **assignment**, not a receipt.

---

## 2. Receipt (Accounting Event)

A **receipt** represents a **real-world payment for a specific month**.

It answers:

> For this month, who actually received money, and how much?

Receipts are:

* Generated **from assignments**
* Monthly
* Immutable once issued
* Used for printing, logs, and taxes

If there is **no receipt**, then **no payment exists**, even if an assignment exists.

---

## 3. Why Assignments and Receipts Must Be Separate

Assignments define **entitlement**.
Receipts record **what actually happened**.

This separation is mandatory because:

* One unit can have multiple owners
* Ownership can alternate over time
* Rent can be split or redirected
* Taxes depend on **actual receipts**, not theoretical ownership

### Correct flow

```
Unit
 └── Assignment(s)  → ownership logic
       └── Receipt(s) → monthly result
```

### Incorrect flow (do NOT do this)

```
Unit → Receipt → Owner   ❌
```

---

## 4. Assignment Table Responsibilities

The `assignments` table must explicitly include the **owner**.

An assignment **cannot infer ownership later**.

Minimum required fields:

* unit_id (FK)
* owner_id (FK)
* share_percent (nullable)
* alternation_type (none / odd_even / cycle)
* cycle_length (nullable)
* cycle_position (nullable)
* start_date
* end_date

This table answers:

> Is this owner entitled to rent for this unit in a given month?

---

## 5. Receipt Table Responsibilities

The `receipts` table records finalized, printable accounting data.

Minimum required fields:

* receipt_id
* assignment_id (FK)
* unit_id (FK)
* owner_id (FK)
* client_id (FK)
* period (YYYY-MM)
* amount
* ras_ir (boolean)
* issued_at

This table answers:

> What was actually paid and logged for this month?

---

## 6. Golden Rules (Non-Negotiable)

* Assignments decide **entitlement**
* Receipts record **reality**
* Receipts are **derived from assignments**
* Assignments never depend on receipts
* Never merge assignments and receipts into one table

Violating these rules will make:

* Alternating ownership impossible
* Tax calculation unreliable
* Historical data inconsistent

---

## 7. Receipt Generation Logic (Conceptual)

For a given month:

1. Load active assignments
2. Evaluate alternation rules
3. Determine eligible owner(s)
4. Compute amount
5. Generate receipt(s)
6. Persist receipts (immutable)

Assignments remain unchanged.

---

This separation is **intentional**, **required**, and **central** to the project design.


