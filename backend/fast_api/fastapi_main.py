# fast_api/fastapi_main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fast_api.routers import snowflake_router, s3_router, summarization_router, rag_router
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = FastAPI(
    title="Document Exploration API",
    description="API for exploring, summarizing, and querying documents.",
    version="1.0.0"
)

# CORS settings (adjust origins if needed)
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the routers
app.include_router(snowflake_router.router)
app.include_router(s3_router.router)
app.include_router(summarization_router.router)
app.include_router(rag_router.router)

# Root endpoint to check if the server is running
@app.get("/")
def read_root():
    return {"message": "Welcome to the Document Exploration API"}
