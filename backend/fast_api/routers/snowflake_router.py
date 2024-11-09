# fast_api/routers/snowflake_router.py

from fastapi import APIRouter, HTTPException
from typing import List
from pydantic import BaseModel
import snowflake.connector
from datetime import datetime
import os

router = APIRouter(
    prefix="/snowflake",
    tags=["Snowflake"]
)

class Publication(BaseModel):
    ID: int
    TITLE: str
    BRIEF_SUMMARY: str
    DATE: str
    AUTHOR: str
    IMAGE_LINK: str = None
    PDF_LINK: str
    RESEARCH_NOTES: str = None
    CREATED_DATE: datetime = None  # Changed to datetime


# Snowflake connection setup (fetch credentials from environment variables)
def get_snowflake_connection():
    try:
        connection = snowflake.connector.connect(
            user=os.getenv("SNOWFLAKE_USER"),
            password=os.getenv("SNOWFLAKE_PASSWORD"),
            account=os.getenv("SNOWFLAKE_ACCOUNT"),
            role=os.getenv("SNOWFLAKE_ROLE"),
            warehouse=os.getenv("SNOWFLAKE_WAREHOUSE", "WH_PUBLICATIONS_ETL"),
            database=os.getenv("SNOWFLAKE_DATABASE", "DB_CFA_PUBLICATIONS"),
            schema=os.getenv("SNOWFLAKE_SCHEMA", "CFA_PUBLICATIONS")
        )
        #print("Connected to Snowflake successfully")  # Debug print
        return connection
    except Exception as e:
        #print(f"Snowflake connection error: {str(e)}")  # Debug print
        raise

@router.get("/publications", response_model=List[Publication])
async def get_publications_from_snowflake():
    """
    Retrieve a list of all publications from Snowflake.
    """
    try:
        conn = get_snowflake_connection()
        cursor = conn.cursor()

        # Use fully qualified table name: {database}.{schema}.{table}
        cursor.execute("SELECT * FROM DB_CFA_PUBLICATIONS.CFA_PUBLICATIONS.PUBLICATION_LIST ORDER BY DATE DESC")
        
        publications = []
        for row in cursor:
            created_date = row[8].strftime("%Y-%m-%d %H:%M:%S") if row[8] else None  # Convert datetime to string
            publications.append(Publication(
                ID=row[0],
                TITLE=row[1],
                BRIEF_SUMMARY=row[2],
                DATE=row[3],
                AUTHOR=row[4],
                IMAGE_LINK=row[5],
                PDF_LINK=row[6],
                RESEARCH_NOTES=row[7],
                CREATED_DATE=created_date  # Use the formatted string
            ))
        cursor.close()
        conn.close()
        
        #print("Fetched publications successfully")  # Debug print
        return publications
    except Exception as e:
        #print(f"Error fetching data from Snowflake: {str(e)}")  # Debug print
        raise HTTPException(status_code=500, detail=f"Error fetching data: {str(e)}")