import boto3
import pymysql
import pandas as pd
from botocore.exceptions import NoCredentialsError

# AWS S3 Configuration
s3 = boto3.client('s3')
bucket_name = "your-s3-bucket"
file_key = "data.csv"

# AWS RDS Configuration
rds_host = "your-rds-endpoint"
rds_user = "your-username"
rds_password = "your-password"
rds_database = "your-database"

# AWS Glue Configuration
glue_client = boto3.client('glue')
glue_database = "your-glue-database"
glue_table = "your-glue-table"

def read_from_s3():
    try:
        obj = s3.get_object(Bucket=bucket_name, Key=file_key)
        df = pd.read_csv(obj['Body'])
        return df
    except NoCredentialsError:
        print("Credentials not available")
        return None

def push_to_rds(df):
    try:
        connection = pymysql.connect(host=rds_host, user=rds_user, password=rds_password, database=rds_database)
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
    response = glue_client.create_table(
        DatabaseName=glue_database,
        TableInput={
            'Name': glue_table,
            'StorageDescriptor': {
                'Columns': [{'Name': 'col1', 'Type': 'string'}, {'Name': 'col2', 'Type': 'string'}],
                'Location': f"s3://{bucket_name}/glue_output/",
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
