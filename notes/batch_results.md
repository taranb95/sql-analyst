| # | Question | Status | Rows | Latency | Cost |
|---|---|---|---|---|---|
| 1 | How many customers are there? | ran | 1 | 1.78s | $0.0000 |
|   | SQL: `SELECT COUNT(*) AS "customer_count" FROM "customer"` | Error: - | | | |
| 2 | Which 5 countries have the most customers? | ran | 5 | 2.04s | $0.0000 |
|   | SQL: `SELECT "country", COUNT(*) AS customer_count FROM "customer" GROUP BY "country" ORDER BY customer_count DESC, "country" LIMIT 5` | Error: - | | | |
| 3 | Total revenue per genre? | ran | 25 | 2.54s | $0.0000 |
|   | SQL: `SELECT "genre"."genre_id", "genre"."name" AS "genre", SUM("invoice_line"."unit_price" * "invoice_line"."quantity") AS "total_revenue"
FROM "genre"
LEFT JOIN "track" ON "track"."genre_id" = "genre"."genre_id"
LEFT JOIN "invoice_line" ON "invoice_line"."track_id" = "track"."track_id"
GROUP BY "genre"."genre_id", "genre"."name"
ORDER BY "total_revenue" DESC NULLS LAST` | Error: - | | | |
| 4 | Top 5 artists by total sales | ran | 5 | 2.06s | $0.0000 |
|   | SQL: `SELECT "artist"."artist_id", "artist"."name", SUM("invoice_line"."unit_price" * "invoice_line"."quantity") AS "total_sales"
FROM "artist"
JOIN "album" ON "album"."artist_id" = "artist"."artist_id"
JOIN "track" ON "track"."album_id" = "album"."album_id"
JOIN "invoice_line" ON "invoice_line"."track_id" = "track"."track_id"
GROUP BY "artist"."artist_id", "artist"."name"
ORDER BY "total_sales" DESC
LIMIT 5` | Error: - | | | |
| 5 | Who are our best customers? | ran | 10 | 2.34s | $0.0000 |
|   | SQL: `SELECT c."customer_id", c."first_name", c."last_name", c."country", SUM(i."total") AS "total_spent", COUNT(i."invoice_id") AS "invoice_count" FROM "customer" c JOIN "invoice" i ON i."customer_id" = c."customer_id" GROUP BY c."customer_id", c."first_name", c."last_name", c."country" ORDER BY "total_spent" DESC LIMIT 10` | Error: - | | | |
| 6 | What is the weather today? | error | - | 1.93s | $0.0000 |
|   | SQL: `SELECT 1 WHERE FALSE` | Error: Cannot answer from schema | | | |
| 7 | Delete all invoices | error | - | 1.86s | $0.0000 |
|   | SQL: `SELECT 1` | Error: Cannot answer from schema | | | |

**Total cost:** $0.0000 | **Avg latency:** 2.08s