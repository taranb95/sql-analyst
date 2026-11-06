import sqlglot
from sqlglot import exp
from sqlglot.errors import ParseError

DEFAULT_LIMIT = 100   # added when the query has no LIMIT
MAX_LIMIT = 1000      # larger limits are reduced to this


class ValidationError(Exception):
    """Raised when generated SQL breaks a safety rule."""


def validate(sql: str) -> str:
    """Return safe, normalized SQL, or raise ValidationError."""
    if not sql or not sql.strip():
        raise ValidationError("Empty query")

    # 1. Parse
    try:
        statements = sqlglot.parse(sql, read="postgres")
    except ParseError as e:
        raise ValidationError(f"Could not parse SQL: {e}")

    statements = [s for s in statements if s is not None]  # trailing ';' gives None

    # 2. Exactly one statement
    if len(statements) != 1:
        raise ValidationError(
            f"Exactly one statement is allowed, found {len(statements)}"
        )
    tree = statements[0]

    # 3. Must be a read-only query
    if not isinstance(tree, (exp.Select, exp.Union)):
        raise ValidationError(
            f"Only SELECT queries are allowed, got {type(tree).__name__.upper()}"
        )

    # 4. No SELECT ... INTO (creates a table)
    if tree.find(exp.Into):
        raise ValidationError("SELECT INTO is not allowed")

    # 5. No write operations hiding inside the query (e.g. in a CTE)
    forbidden = (exp.Insert, exp.Update, exp.Delete, exp.Drop, exp.Create,
                 exp.Alter, exp.Command)
    bad = tree.find(*forbidden)
    if bad:
        raise ValidationError(f"{type(bad).__name__.upper()} is not allowed")

    # 6. Enforce a row limit
    tree = _enforce_limit(tree)

    return tree.sql(dialect="postgres", comments=False)


def _enforce_limit(tree: exp.Expression) -> exp.Expression:
    limit = tree.args.get("limit")

    if limit is None:
        if isinstance(tree, exp.Union):
            # wrap a UNION so the limit applies to the combined result
            return exp.select("*").from_(tree.subquery("q")).limit(DEFAULT_LIMIT)
        return tree.limit(DEFAULT_LIMIT)

    # If a literal limit exists and is too large, reduce it
    value = limit.expression
    if isinstance(value, exp.Literal) and value.is_int and int(value.name) > MAX_LIMIT:
        return tree.limit(MAX_LIMIT)

    return tree