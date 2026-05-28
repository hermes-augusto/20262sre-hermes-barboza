import os
import time
import clickhouse_connect
import boto3
from io import BytesIO

CLICKHOUSE_HOST = os.getenv("CLICKHOUSE_HOST", "clickhouse")
CLICKHOUSE_PORT = int(os.getenv("CLICKHOUSE_PORT", "8123"))
CLICKHOUSE_USER = os.getenv("CLICKHOUSE_USER", "ingest")
CLICKHOUSE_PASSWORD = os.getenv("CLICKHOUSE_PASSWORD", "ingest")
S3_BUCKET = os.getenv("S3_BUCKET_NAME", "olist")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")

TABLES = {
    "olist_orders_dataset": "orders",
    "olist_order_items_dataset": "order_items",
    "olist_order_payments_dataset": "order_payments",
    "olist_order_reviews_dataset": "order_reviews",
    "olist_products_dataset": "products",
    "olist_sellers_dataset": "sellers",
    "olist_customers_dataset": "customers",
    "olist_geolocation_dataset": "geolocation",
}


def get_clickhouse_client():
    return clickhouse_connect.get_client(
        host=CLICKHOUSE_HOST,
        port=CLICKHOUSE_PORT,
        username=CLICKHOUSE_USER,
        password=CLICKHOUSE_PASSWORD,
    )


def get_s3_client():
    return boto3.client("s3", region_name=AWS_REGION)


def create_database(client):
    client.command("CREATE DATABASE IF NOT EXISTS olist")


def create_table(client, table_name, csv_columns):
    col_defs = ", ".join([f"{col} String" for col in csv_columns])
    client.command(f"""
        CREATE TABLE IF NOT EXISTS olist.{table_name}
        ({col_defs})
        ENGINE = MergeTree()
        ORDER BY tuple()
    """)


def ingest_table(ch_client, s3_client, s3_key, table_name):
    try:
        response = s3_client.get_object(Bucket=S3_BUCKET, Key=f"{s3_key}.csv")
        csv_data = response["Body"].read().decode("utf-8")

        lines = csv_data.strip().split("\n")
        if len(lines) < 2:
            print(f"  Arquivo {s3_key}.csv vazio ou sem dados")
            return

        headers = [h.strip().strip('"') for h in lines[0].split(",")]
        create_table(ch_client, table_name, headers)

        rows = []
        for line in lines[1:]:
            values = [v.strip().strip('"') for v in line.split(",")]
            if len(values) == len(headers):
                rows.append(values)

        if rows:
            col_defs = ", ".join([f"`{h}` String" for h in headers])
            ch_client.insert(
                f"olist.{table_name}",
                rows,
                column_names=headers,
            )
            print(f"  Ingested {len(rows)} rows into {table_name}")
        else:
            print(f"  Nenhuma linha válida encontrada em {s3_key}.csv")

    except Exception as e:
        print(f"  Erro ao ingerir {s3_key}: {e}")


def main():
    print("Iniciando ingestão de dados do S3 para ClickHouse...")

    ch_client = get_clickhouse_client()
    s3_client = get_s3_client()

    create_database(ch_client)

    for s3_key, table_name in TABLES.items():
        print(f"Processando {s3_key}...")
        ingest_table(ch_client, s3_client, s3_key, table_name)

    print("Ingestão concluída!")


if __name__ == "__main__":
    main()
