from app.validator import validate, ValidationError

cases = [
    # (label, sql, should_pass)
    ("simple select",        "SELECT * FROM customer", True),
    ("trailing semicolon",   "SELECT * FROM customer;", True),
    ("join + group by",      "SELECT country, COUNT(*) FROM customer GROUP BY country", True),
    ("CTE select",           "WITH t AS (SELECT * FROM customer) SELECT * FROM t", True),
    ("union",                "SELECT first_name FROM customer UNION SELECT first_name FROM employee", True),
    ("has limit",            "SELECT * FROM customer LIMIT 5", True),
    ("huge limit",           "SELECT * FROM customer LIMIT 999999", True),
    ("word delete in text",  "SELECT * FROM customer WHERE company = 'delete me'", True),
    ("delete",               "DELETE FROM invoice", False),
    ("drop",                 "DROP TABLE customer", False),
    ("update",               "UPDATE customer SET country = 'X'", False),
    ("insert",               "INSERT INTO genre (name) VALUES ('x')", False),
    ("two statements",       "SELECT 1; DROP TABLE customer", False),
    ("select into",          "SELECT * INTO backup FROM customer", False),
    ("delete in a CTE",      "WITH d AS (DELETE FROM invoice RETURNING *) SELECT * FROM d", False),
    ("garbage",              "hello world this is not sql", False),
    ("empty",                "", False),
]

for label, sql, should_pass in cases:
    try:
        out = validate(sql)
        result = "PASSED"
        detail = out
    except ValidationError as e:
        result = "BLOCKED"
        detail = str(e)
    ok = (result == "PASSED") == should_pass
    print(f"{'OK  ' if ok else 'FAIL'} {label:22} {result:8} {detail}")