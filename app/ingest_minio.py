import os
import sys
import time
import json
import boto3
import pandas as pd
import clickhouse_connect
from datetime import datetime

def get_clickhouse_client():
    host = os.getenv('CLICKHOUSE_HOST', 'clickhouse')
    port = int(os.getenv('CLICKHOUSE_PORT', 8123))
    user = os.getenv('CLICKHOUSE_USER', 'default')
    password = os.getenv('CLICKHOUSE_PASSWORD', 'password123')
    
    for i in range(10):
        try:
            client = clickhouse_connect.get_client(
                host=host,
                port=port,
                username=user,
                password=password
            )
            print("INFO: Successfully connected to ClickHouse.")
            return client
        except Exception as e:
            print(f"WAIT: Attempt {i+1}/10 - Waiting for ClickHouse at {host}:{port}... ({e})")
            time.sleep(5)
    sys.exit(1)

def get_s3_client():
    endpoint = os.getenv('S3_ENDPOINT_URL', 'http://minio:9000')
    for i in range(10):
        try:
            s3 = boto3.client(
                's3',
                endpoint_url=endpoint,
                aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID', 'admin'),
                aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY', 'password123'),
                region_name='us-east-1'
            )
            s3.list_buckets()
            print("INFO: Successfully connected to MinIO.")
            return s3
        except Exception as e:
            print(f"WAIT: Attempt {i+1}/10 - Waiting for MinIO at {endpoint}... ({e})")
            time.sleep(5)
    sys.exit(1)

def init_db(client):
    sql_files = [
        '/app/sql/raw/01_schema.sql',
        '/app/sql/views/01_top_products.sql'
    ]
    
    for sql_file in sql_files:
        if not os.path.exists(sql_file):
            alt_path = sql_file.replace('/app/', '')
            if os.path.exists(alt_path): sql_file = alt_path
            else: continue
            
        try:
            with open(sql_file, 'r') as f:
                sql_content = f.read()
                for command in sql_content.split(';'):
                    if command.strip():
                        client.command(command)
            print(f"SUCCESS: Initialized {sql_file}")
        except Exception as e:
            print(f"FAILED: Error executing {sql_file}: {e}")

def ingest_file(s3, ch, bucket, key):
    print(f"INFO: Starting ingestion for file: {key}")
    try:
        obj = s3.get_object(Bucket=bucket, Key=key)
        df = pd.read_csv(obj['Body'])
    except Exception as e:
        print(f"ERROR: Could not read file {key}: {e}")
        return

    now_ts = int(time.time())
    records = []
    batch_size = 20000
    total_rows = len(df)
    
    for i, (_, row) in enumerate(df.iterrows()):
        # Voltamos a salvar como String JSON para estabilidade
        records.append([now_ts, row.to_json(), key])
        
        if len(records) >= batch_size:
            ch.insert('olist_raw.ingestion', records, column_names=['unixtime', 'data', 'tag'])
            records = []
            print(f"INFO: Progress {key}: {i+1}/{total_rows} rows inserted.")

    if records:
        ch.insert('olist_raw.ingestion', records, column_names=['unixtime', 'data', 'tag'])
    
    print(f"SUCCESS: Finished {key} ({total_rows} rows)")

def main():
    s3 = get_s3_client()
    ch = get_clickhouse_client()
    init_db(ch)
    
    bucket_name = os.getenv('S3_BUCKET_NAME', 'olist')
    processed_keys = set()
    
    print(f"INFO: Monitoring bucket '{bucket_name}'...")
    
    while True:
        try:
            response = s3.list_objects_v2(Bucket=bucket_name)
            if 'Contents' in response:
                for obj in response['Contents']:
                    key = obj['Key']
                    if key.endswith('.csv') and key not in processed_keys:
                        ingest_file(s3, ch, bucket_name, key)
                        processed_keys.add(key)
        except Exception as e:
            print(f"WARNING: Loop error: {e}")
        time.sleep(10)

if __name__ == "__main__":
    main()
