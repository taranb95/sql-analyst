import re
import time
from time import monotonic
from anthropic import Anthropic
from sqlalchemy import text
from dotenv import load_dotenv

from app.schema import engine, load_schema, get_table_names
from app.prompts import SYSTEM_PROMPT
from app.validator import validate, ValidationError

load_dotenv()
client = Anthropic()
MODEL = "claude-sonnet-5-5"


SQL_TOOL = {
    "name": "submit_sql",
    "description": "Submit the SQL query that answers the question.",
    "input_schema": {
        "type": "object",
        "properties": {
            "sql": {"type": "string", "description": "A single PostgreSQL SELECT query"},
            "answerable": {"type": "boolean", "description": "False if the schema cannot answer the question"},
            "reasoning": {"type": "string", "description": "One sentence on the approach"},
        },
        "required": ["sql", "answerable"],
    },
}

# Fill these in from the pricing page (USD per 1 million tokens)
PRICE_PER_M_INPUT = 0.0   # TODO: replace with your model's input price
PRICE_PER_M_OUTPUT = 0.0  # TODO: replace with your model's output price


def estimate_cost(input_tokens: int, output_tokens: int) -> float:
    return (
        input_tokens * PRICE_PER_M_INPUT + output_tokens * PRICE_PER_M_OUTPUT
    ) / 1_000_000

def generate_sql_structured(question: str, schema: str) -> dict:
    resp = client.messages.create(
        model=MODEL,
        max_tokens=600,
        #temperature=0,
        system=SYSTEM_PROMPT.format(schema=schema),
        tools=[SQL_TOOL],
        # tool_choice={"type": "tool", "name": "submit_sql"},
        messages=[{"role": "user", "content": question}],
    )
    for block in resp.content:
        if block.type == "tool_use":
            result = dict(block.input)
            result["usage"] = resp.usage
            return result
    raise ValueError(
        f"No tool call returned. Block types: {[b.type for b in resp.content]}. "
        f"Text: {get_text(resp)[:200]}"
    )

def get_text(resp) -> str:
    """Join all text blocks, ignoring thinking and other block types."""
    return "".join(b.text for b in resp.content if b.type == "text")

def clean_sql(raw: str) -> str:
    """Strip markdown fences if the model adds them anyway."""
    raw = raw.strip()
    raw = re.sub(r"^```(?:sql)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)
    return raw.strip().rstrip(";")


def generate_sql(question: str, schema: str) -> str:
    resp = client.messages.create(
        model=MODEL,
        max_tokens=500,
        system=SYSTEM_PROMPT.format(schema=schema),
        messages=[{"role": "user", "content": question}],
    )
    return clean_sql(get_text(resp))


def run_sql(sql: str) -> list[dict]:
    with engine.connect() as conn:
        result = conn.execute(text(sql))
        return [dict(row._mapping) for row in result]


def ask(question: str) -> dict:
    schema = load_schema()
    start = monotonic()
    try:
        gen = generate_sql_structured(question, schema)
    except Exception as e:
        return {"question": question, "sql": None, "error": f"LLM error: {e}"}
    latency = round(monotonic() - start, 2)

    usage = gen.get("usage")
    base = {
        "question": question,
        "sql": gen.get("sql"),
        "reasoning": gen.get("reasoning"),
        "latency_s": latency,
        "tokens": (usage.input_tokens, usage.output_tokens) if usage else None,
        "cost_usd": estimate_cost(usage.input_tokens, usage.output_tokens) if usage else None,  # NEW
    }

    if not gen.get("answerable", True):
        return {**base, "error": "Cannot answer from schema"}

    try:
        safe_sql = validate(gen["sql"], allowed_tables=get_table_names())
    except ValidationError as e:
        return {**base, "blocked": True, "error": f"Blocked by validator: {e}"}

    try:
        rows = run_sql(safe_sql)
        return {**base, "sql": safe_sql, "rows": rows}
    except Exception as e:
        return {**base, "sql": safe_sql, "error": str(e)}
    
# def ask(question: str) -> dict:

#     base = {
#     "question": question,
#     "sql": gen.get("sql"),
#     "reasoning": gen.get("reasoning"),
#     "latency_s": latency,
#     "tokens": (usage.input_tokens, usage.output_tokens) if usage else None,
#     "cost_usd": estimate_cost(usage.input_tokens, usage.output_tokens) if usage else None,
# }
    
#     schema = load_schema()
#     #sql = generate_sql(question, schema)
#     sql = generate_sql_structured(question, schema)
#     if sql == "CANNOT_ANSWER":
#         return {"question": question, "sql": None, "error": "Cannot answer from schema"}
#     try:
#         rows = run_sql(sql)
#         return {"question": question, "sql": sql, "rows": rows}
#     except Exception as e:
#         return {"question": question, "sql": sql, "error": str(e)}


if __name__ == "__main__":
    while True:
        q = input("\nAsk a question (or 'quit'): ").strip()
        if q.lower() == "quit":
            break
        out = ask(q)
        print("\nSQL:", out["sql"])
        if "error" in out:
            print("Error:", out["error"])
        else:
            for row in out["rows"][:20]:
                print(row)
            print(f"({len(out['rows'])} rows)")
        cost = out.get("cost_usd")
        cost_str = f"${cost:.4f}" if cost is not None else "n/a"
        print(f"Latency: {out.get('latency_s', 'n/a')}s | Tokens (in, out): {out.get('tokens', 'n/a')} | Cost: {cost_str}")