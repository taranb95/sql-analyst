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


if __name__ == "__main__":
    print(load_schema())