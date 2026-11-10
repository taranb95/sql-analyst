import pytest
from app.validator import validate, ValidationError

ALLOWED = {"customer", "invoice", "invoice_line", "track", "genre", "album", "artist"}


# --- Queries that must pass ---
@pytest.mark.parametrize("sql", [
    "SELECT * FROM customer",
    "SELECT * FROM customer;",
    "SELECT country, COUNT(*) FROM customer GROUP BY country",
    "SELECT c.first_name FROM customer c JOIN invoice i ON i.customer_id = c.customer_id",
    "WITH t AS (SELECT * FROM customer) SELECT * FROM t",
    "SELECT * FROM customer WHERE company = 'delete me'",
    "SELECT * FROM customer WHERE customer_id IN (SELECT customer_id FROM invoice)",
    'SELECT * FROM "customer"',
    "SELECT * FROM public.customer",
])
def test_allowed_queries_pass(sql):
    validate(sql, allowed_tables=ALLOWED)


# --- Queries that must be blocked ---
@pytest.mark.parametrize("sql", [
    "DELETE FROM invoice",
    "DROP TABLE customer",
    "UPDATE customer SET country = 'X'",
    "INSERT INTO genre (name) VALUES ('x')",
    "SELECT 1; DROP TABLE customer",
    "SELECT * INTO backup FROM customer",
    "WITH d AS (DELETE FROM invoice RETURNING *) SELECT * FROM d",
    "hello world this is not sql",
    "",
    "SELECT * FROM employee",
    "SELECT * FROM pg_shadow",
    "SELECT * FROM pg_catalog.pg_shadow",
    "SELECT * FROM information_schema.columns",
    "SELECT * FROM customer JOIN secret_table ON true",
    "SELECT * FROM customer WHERE customer_id IN (SELECT id FROM secret_table)",
    "SELECT pg_sleep(100)",
    "SELECT * FROM customer WHERE customer_id = (SELECT 1 FROM pg_sleep(5))",
])
def test_bad_queries_are_blocked(sql):
    with pytest.raises(ValidationError):
        validate(sql, allowed_tables=ALLOWED)


# --- Limit behavior ---
def test_limit_added_when_missing():
    out = validate("SELECT * FROM customer", allowed_tables=ALLOWED)
    assert "LIMIT 100" in out.upper()


def test_small_limit_kept():
    out = validate("SELECT * FROM customer LIMIT 5", allowed_tables=ALLOWED)
    assert "LIMIT 5" in out.upper()


def test_huge_limit_reduced():
    out = validate("SELECT * FROM customer LIMIT 999999", allowed_tables=ALLOWED)
    assert "LIMIT 1000" in out.upper()
    assert "999999" not in out