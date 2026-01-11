# DB path and settings
DB_PATH = 'database.db'

# Tax configuration (editable per-year)
TAX_CONFIG = {
    # fraction to keep after 40% abattement: taxable = gross * (1 - abattement)
    'abattement': 0.40,

    # IR brackets applied to the taxable amount (min, max, rate, deduction)
    # max == None means no upper bound
    'ir_brackets': [
        (0, 40000, 0.00, 0),
        (40001, 60000, 0.10, 4000),
        (60001, 80000, 0.20, 10000),
        (80001, 100000, 0.30, 18000),
        (100001, 180000, 0.34, 22000),
        (180001, None, 0.37, 27400),
    ],

    # RAS thresholds (based on annual gross revenue), list of (min, max, rate)
    'ras_thresholds': [
        (0, 40000, 0.00),
        (40001, 119999, 0.10),
        (120000, None, 0.15),
    ],

    # Family deduction: per person and maximum
    'family_deduction_per_person': 500,
    'family_deduction_max': 3000,
}
