import snowflake.connector
import boto3
import os
import pandas as pd
from io import StringIO
from dotenv import load_dotenv

load_dotenv()

# Establish a connection to Snowflake using environment variables
conn = snowflake.connector.connect(
    user=os.getenv("SNOWFLAKE_USER"),
    password=os.getenv("SNOWFLAKE_PASSWORD"),
    account=os.getenv("SNOWFLAKE_ACCOUNT"),
    warehouse=os.getenv("SNOWFLAKE_WAREHOUSE", "WH_PUBLICATIONS_ETL"),
    role=os.getenv("SNOWFLAKE_ROLE")
)

# Create a cursor
cursor = conn.cursor()

# Get the database, schema, and table names from environment variables, or use default values
database_name = os.getenv("SNOWFLAKE_DATABASE", "DB_CFA_PUBLICATIONS")
schema_name = os.getenv("SNOWFLAKE_SCHEMA", "CFA_PUBLICATIONS")
table_name = os.getenv("SNOWFLAKE_TABLE", "PUBLICATION_LIST")

# S3 configurations from environment variables
s3_bucket = os.getenv("S3_BUCKET_NAME")
s3_key = "raw/publications_data.csv"
aws_region = os.getenv("AWS_REGION")

# Initialize the S3 client
s3_client = boto3.client(
    's3',
    region_name=aws_region,
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
)

def read_csv_from_s3(bucket, key):
    """Read a CSV file from S3 and return a pandas DataFrame."""
    response = s3_client.get_object(Bucket=bucket, Key=key)
    csv_content = response['Body'].read().decode('utf-8')
    
    # Read CSV into a DataFrame
    df = pd.read_csv(StringIO(csv_content))
    
    # Strip any leading/trailing spaces in column names
    df.columns = df.columns.str.strip()

    # Check column names and print them for debugging
    print(f"DataFrame columns: {df.columns.tolist()}")

    return df


def insert_data_into_snowflake(df):
    """Insert a pandas DataFrame into Snowflake using a merge operation."""
    cursor = conn.cursor()

    # Replace NaN values with None to avoid SQL errors
    df = df.where(pd.notnull(df), None)

    try:
        for index, row in df.iterrows():
            merge_query = f"""
            MERGE INTO {database_name}.{schema_name}.{table_name} AS target
            USING (SELECT '{row['title']}' AS TITLE,
                         '{row['summary']}' AS BRIEF_SUMMARY,
                         '{row['date']}' AS DATE,
                         '{row['authors']}' AS AUTHOR,
                         '{row['cover_path']}' AS IMAGE_LINK,
                         '{row['publication_path']}' AS PDF_LINK) AS source
            ON target.TITLE = source.TITLE
               AND target.AUTHOR = source.AUTHOR
               AND target.DATE = source.DATE
            WHEN MATCHED THEN
              UPDATE SET target.BRIEF_SUMMARY = source.BRIEF_SUMMARY,
                         target.IMAGE_LINK = source.IMAGE_LINK,
                         target.PDF_LINK = source.PDF_LINK
            WHEN NOT MATCHED THEN
              INSERT (TITLE, BRIEF_SUMMARY, DATE, AUTHOR, IMAGE_LINK, PDF_LINK)
              VALUES (source.TITLE, source.BRIEF_SUMMARY, source.DATE, source.AUTHOR, source.IMAGE_LINK, source.PDF_LINK);
            """
            cursor.execute(merge_query)

        print(f"Successfully merged {len(df)} rows into '{table_name}'.")

    except snowflake.connector.errors.ProgrammingError as e:
        print(f"Error during data merge: {e}")

    finally:
        cursor.close()

def main():
    try:
        # Read the CSV from S3
        print(f"Reading CSV file from S3 bucket '{s3_bucket}'...")
        df = read_csv_from_s3(s3_bucket, s3_key)
        print(f"Successfully read {len(df)} rows from the CSV file.")

        # Insert data into Snowflake
        print(f"Inserting data into Snowflake table '{table_name}'...")
        insert_data_into_snowflake(df)
        print("Data insertion completed.")

    except Exception as e:
        print(f"Error in processing: {e}")

    finally:
        # Close the Snowflake connection
        conn.close()
        print("Snowflake connection closed.")

if __name__ == "__main__":
    main()
