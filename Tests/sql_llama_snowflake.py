# Step 1: Import necessary modules
from sqlalchemy import create_engine
from urllib.parse import quote_plus
from llama_index.core import SQLDatabase, ServiceContext, GPTVectorStoreIndex, Document
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.langchain import LangChainLLM
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import openai
import os

# Load environment variables from the .env file
load_dotenv()

# Step 2: Set up OpenAI API Key and Snowflake Credentials (replace with your actual details)
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
SNOWFLAKE_USER = os.getenv('SNOWFLAKE_USER')
SNOWFLAKE_PASSWORD = os.getenv('SNOWFLAKE_PASSWORD')
SNOWFLAKE_ACCOUNT = os.getenv('SNOWFLAKE_ACCOUNT')
SNOWFLAKE_WAREHOUSE = os.getenv('SNOWFLAKE_WAREHOUSE')
SNOWFLAKE_DATABASE = os.getenv('SNOWFLAKE_DATABASE')
SNOWFLAKE_SCHEMA = os.getenv('SNOWFLAKE_SCHEMA')


# Step 3: Establish Snowflake Connection using SQLAlchemy
connection_string = f"snowflake://{SNOWFLAKE_USER}:{quote_plus(SNOWFLAKE_PASSWORD)}@{SNOWFLAKE_ACCOUNT}/{SNOWFLAKE_DATABASE}/{SNOWFLAKE_SCHEMA}?warehouse={SNOWFLAKE_WAREHOUSE}&role=ACCOUNTADMIN"
engine = create_engine(connection_string)
sql_database = SQLDatabase(engine)

# Step 4: Configure OpenAI and LLM Settings
openai.api_key = OPENAI_API_KEY
chat_openai = ChatOpenAI(
    temperature=0,
    openai_api_key=OPENAI_API_KEY,
    model_name="gpt-3.5-turbo"
)

# Step 5: Set up LangChain LLM and Embedding Model
langchain_llm = LangChainLLM(llm=chat_openai)
embedding_model = OpenAIEmbedding(model="text-embedding-ada-002", openai_api_key=OPENAI_API_KEY)

# Step 6: Define a Custom ServiceContext Class
class ServiceContext:
    def __init__(self, llm_predictor):
        self.llm_predictor = llm_predictor

    @classmethod
    def from_defaults(cls, llm_predictor=None):
        if llm_predictor is None:
            llm_predictor = langchain_llm
        return cls(llm_predictor=llm_predictor)

# Create the ServiceContext object
service_context = ServiceContext.from_defaults(llm_predictor=langchain_llm)

# Step 7: Create the Index and Load Data from Snowflake
# SQL Query to fetch relevant data from the Snowflake table
from sqlalchemy import text  # Import text for raw SQL queries

# SQL Query to fetch relevant data from the Snowflake table
fetch_query = text("""
SELECT TITLE, BRIEF_SUMMARY, AUTHOR FROM PUBLICATION_LIST;
""")

# Execute the SQL query and fetch the results as dictionaries
with engine.connect() as conn:
    result = conn.execute(fetch_query)
    rows = result.mappings().all()  # Fetch rows as dictionaries

    # Print the first row to inspect column names
    if rows:
        print("First row keys:", rows[0].keys())

# Convert fetched rows into LlamaIndex Documents using dictionary keys
# Convert fetched rows into LlamaIndex Documents using correct lowercase keys
documents = [
    Document(
        text=f"Title: {row['title']}\nSummary: {row['brief_summary']}\nAuthor: {row['author']}"
    )
    for row in rows
]


# Create and load data into the GPTVectorStoreIndex
index = GPTVectorStoreIndex(
    documents,  # Insert the documents into the index
    sql_database=sql_database,
    service_context=service_context
)

# Step 8: Query the Index for Authors (Based on Title)
query_engine = index.as_query_engine()
response = query_engine.query("give all the authors for the title Capitalism for Everyone")
print("Authors for 'Capitalism for Everyone':", response)


































































































#






























































































































































































































































































#end


















#