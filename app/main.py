import os
import boto3
import pymysql
import pandas as pd
from botocore.exceptions import NoCredentialsError

# Read AWS credentials from environment variables
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
S3_FILE_KEY = os.getenv("S3_FILE_KEY")

RDS_HOST = os.getenv("RDS_HOST")
RDS_USER = os.getenv("RDS_USER")
RDS_PASSWORD = os.getenv("RDS_PASSWORD")
RDS_DATABASE = os.getenv("RDS_DATABASE")

GLUE_DATABASE = os.getenv("GLUE_DATABASE")
GLUE_TABLE = os.getenv("GLUE_TABLE")

# AWS Clients
s3 = boto3.client('s3', region_name=AWS_REGION)
glue_client = boto3.client('glue', region_name=AWS_REGION)

def read_from_s3():
    try:
        obj = s3.get_object(Bucket=S3_BUCKET_NAME, Key=S3_FILE_KEY)
        df = pd.read_csv(obj['Body'])
        return df
    except NoCredentialsError:
        print("AWS Credentials not found. Use IAM roles or environment variables.")
        return None

def push_to_rds(df):
    try:
        connection = pymysql.connect(
            host=RDS_HOST, user=RDS_USER, password=RDS_PASSWORD, database=RDS_DATABASE
        )
        cursor = connection.cursor()
        for _, row in df.iterrows():
            cursor.execute("INSERT INTO your_table (col1, col2) VALUES (%s, %s)", (row['col1'], row['col2']))
        connection.commit()
        connection.close()
        print("Data successfully pushed to RDS")
    except Exception as e:
        print(f"Failed to push data to RDS: {e}")
        return False
    return True

def push_to_glue(df):
    glue_client.create_table(
        DatabaseName=GLUE_DATABASE,
        TableInput={
            'Name': GLUE_TABLE,
            'StorageDescriptor': {
                'Columns': [{'Name': 'col1', 'Type': 'string'}, {'Name': 'col2', 'Type': 'string'}],
                'Location': f"s3://cicd-proj/glue_output/",
                'InputFormat': 'org.apache.hadoop.mapred.TextInputFormat',
                'OutputFormat': 'org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat',
                'SerdeInfo': {'SerializationLibrary': 'org.apache.hadoop.hive.serde2.lazy.LazySimpleSerDe'}
            }
        }
    )
    print("Data pushed to Glue")

def main():
    df = read_from_s3()
    if df is not None:
        if not push_to_rds(df):
            push_to_glue(df)

if __name__ == "__main__":
    main()
