import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()
engine = create_engine(os.environ["DATABASE_URL"])


def load_schema() -> str:
    query = text("""
        SELECT table_name, column_name, data_type
        FROM information_schema.columns
        WHERE table_schema = 'public'
        ORDER BY table_name, ordinal_position
    """)
    tables: dict[str, list[str]] = {}
    with engine.connect() as conn:
        for table, column, dtype in conn.execute(query):
            tables.setdefault(table, []).append(f'"{column}" {dtype}')
    return "\n".join(
        f'TABLE "{t}" ({", ".join(cols)})' for t, cols in tables.items()
    )

def get_table_names() -> set[str]:
    """Names of tables the assistant is allowed to query (lowercased)."""
    query = text("""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
    """)
    with engine.connect() as conn:
        return {row[0].lower() for row in conn.execute(query)}
    
if __name__ == "__main__":
    print(load_schema())