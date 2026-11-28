import csv
import json

import duckdb

from config import EMBED_MODEL, INDEX_PATH, embed_client

con = duckdb.connect("warehouse.duckdb", read_only=True)

docs = [f"gold.daily_revenue {d} : chiffre d'affaires {r} EUR, {n} commandes"
        for d, r, n in con.execute("SELECT order_date, revenue_eur, orders FROM gold.daily_revenue").fetchall()]
# TODO : une phrase "Meilleur jour de ventes : <date>, avec <CA> EUR" (calculée en SQL)
best_day = con.execute(
    "SELECT order_date, revenue_eur FROM gold.daily_revenue "
    "ORDER BY revenue_eur DESC LIMIT 1"
).fetchone()
docs.append(f"Meilleur jour de ventes : {best_day[0]}, avec {best_day[1]} EUR")
# TODO : une phrase "Chiffre d'affaires total : <total> EUR"
total_revenue = con.execute(
    "SELECT SUM(revenue_eur) FROM gold.daily_revenue"
).fetchone()[0]
docs.append(f"Chiffre d'affaires total : {total_revenue} EUR")
# TODO : une phrase par client du top 10 (nom, pays, nombre de commandes, CA) et une phrase "Meilleur client : ..."
tables = con.execute(
    "SELECT table_name FROM information_schema.tables "
    "WHERE table_schema = 'gold'"
).fetchall()
aliases = {
    "name": ("customer_name", "client_name", "name"),
    "country": ("customer_country", "client_country", "country"),
    "orders": ("orders", "order_count", "number_of_orders", "total_orders"),
    "revenue": ("revenue_eur", "total_revenue", "revenue", "ca_eur"),
}
customer_table = None
customer_columns = None
for (table_name,) in tables:
    columns = {
        row[0].lower()
        for row in con.execute(
            f'SELECT * FROM gold."{table_name}" LIMIT 0'
        ).description
    }
    found = {}
    for field, names in aliases.items():
        found[field] = next((name for name in names if name in columns), None)
    if all(found.values()):
        customer_table = table_name
        customer_columns = found
        break

if customer_table is not None:
    name = customer_columns["name"]
    country = customer_columns["country"]
    orders = customer_columns["orders"]
    revenue = customer_columns["revenue"]
    customers = con.execute(
        f'Select "{name}", "{country}", "{orders}", "{revenue}" '
        f'FROM gold."{customer_table}" '
        f'ORDER BY "{revenue}" DESC LIMIT 10'
    ).fetchall()
    for customer_name, customer_country, order_count, revenue_eur in customers:
        docs.append(
            f"gold.{customer_table} : client {customer_name}, pays {customer_country}, "
            f"{order_count} commandes, CA {revenue_eur} EUR"
        )
    if customers:
        customer_name, customer_country, order_count, revenue_eur = customers[0]
        docs.append(
            f"Meilleur client : {customer_name}, pays {customer_country}, "
            f"{order_count} commandes, CA {revenue_eur} EUR"
        )
# TODO : une phrase par ligne de quality_report.csv
with open("quality_report.csv", newline="", encoding="utf-8") as report_file:
    for row in csv.DictReader(report_file):
        docs.append(
            "quality_report.csv : "
            + ", ".join(f"{key}={value}" for key, value in row.items())
        )

vectors = [item.embedding for item in embed_client.embeddings.create(model=EMBED_MODEL, input=docs).data]
with open(INDEX_PATH, "w") as f:
    json.dump({"docs": docs, "vectors": vectors}, f)
print(f"Indexed {len(docs)} chunks")