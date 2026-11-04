## How it works
Question → schema + prompt → LLM returns SQL via tool call → run on a read-only DB role → results.

## Run
1. `docker compose up -d` and load `data/Chinook_PostgreSql.sql`
2. Create the read-only role (see notes)
3. Copy `.env.example` to `.env` and fill in your keys
4. `pip install -r requirements.txt`
5. `python -m app.pipeline`

## Week 2 results
- Questions tested: N
- Correct: X | Wrong: Y | Error: Z | Refused: W
- Avg latency: __s | Avg cost per question: $__
- Main failure patterns: (e.g. multi-table joins, ambiguous wording)