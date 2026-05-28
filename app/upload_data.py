import os
import boto3
import glob

def upload_bootstrap():
    s3_endpoint = os.getenv('S3_ENDPOINT_URL', 'http://minio:9000')
    bucket_name = os.getenv('S3_BUCKET_NAME', 'olist')
    access_key = os.getenv('AWS_ACCESS_KEY_ID', 'admin')
    secret_key = os.getenv('AWS_SECRET_ACCESS_KEY', 'password123')

    s3 = boto3.client(
        's3',
        endpoint_url=s3_endpoint,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name='us-east-1'
    )

    # Garante que o bucket existe
    try:
        s3.head_bucket(Bucket=bucket_name)
    except:
        print(f"Creating bucket {bucket_name}...")
        s3.create_bucket(Bucket=bucket_name)

    # Procura CSVs na pasta raiz /data (onde o docker mapeou)
    csv_files = glob.glob("/data/*.csv")
    
    if not csv_files:
        print("No CSV files found in /data to upload.")
        return

    for file_path in csv_files:
        file_name = os.path.basename(file_path)
        print(f"Uploading {file_name} to MinIO...")
        try:
            s3.upload_file(file_path, bucket_name, file_name)
            print(f"Successfully uploaded {file_name}")
        except Exception as e:
            print(f"Failed to upload {file_name}: {e}")

if __name__ == "__main__":
    upload_bootstrap()
