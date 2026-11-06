# import time
# from app.pipeline import ask

# with open("scratch/questions.txt") as f:
#     questions = [line.strip() for line in f if line.strip()]

# results = []
# for q in questions:
#     out = ask(q)
#     results.append(out)
#     time.sleep(0.5)  # be gentle with rate limits

# total_cost = sum(r.get("cost_usd") or 0 for r in results)
# total_latency = sum(r["latency_s"] for r in results if "latency_s" in r)

# lines = ["| # | Question | Status | Rows | Latency | Cost |", "|---|---|---|---|---|---|"]
# for i, r in enumerate(results, 1):
#     status = "error" if "error" in r else "ran"
#     rows = len(r["rows"]) if "rows" in r else "-"
#     lat = f"{r.get('latency_s', 0)}s"
#     cost = f"${r['cost_usd']:.4f}" if r.get("cost_usd") is not None else "-"
#     lines.append(f"| {i} | {r['question']} | {status} | {rows} | {lat} | {cost} |")
#     lines.append(f"|   | SQL: `{r.get('sql')}` | Error: {r.get('error', '-')} | | | |")

# lines.append("")
# lines.append(f"**Total cost:** ${total_cost:.4f} | **Avg latency:** {total_latency / len(results):.2f}s")

# report = "\n".join(lines)
# print(report)
# with open("notes/batch_results.md", "w") as f:
#     f.write(report)

import sqlglot

tree = sqlglot.parse_one("SELECT name FROM customer WHERE country = 'Canada'", read="postgres")
print(type(tree))      # <class 'sqlglot.expressions.Select'>
print(repr(tree))      # shows the tree structure

for stmt in sqlglot.parse("SELECT 1; DROP TABLE customer", read="postgres"):
    print(type(stmt))  # Select, then Drop