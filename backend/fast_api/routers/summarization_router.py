# fast_api/routers/summarization_router.py

from pydantic import BaseModel
from fastapi import APIRouter, HTTPException
from langchain_nvidia_ai_endpoints import ChatNVIDIA
import boto3
import os

router = APIRouter(
    prefix="/summarization",
    tags=["Summarization"]
)

# Define a model for the JSON payload
class SummaryRequest(BaseModel):
    pdf_link: str

# Initialize S3 client using environment variables
s3_client = boto3.client(
    's3',
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_REGION")
)

def get_s3_file_content(bucket_name, file_key):
    """Helper function to fetch file content from S3."""
    try:
        response = s3_client.get_object(Bucket=bucket_name, Key=file_key)
        file_content = response['Body'].read().decode('utf-8')
        return file_content
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching file from S3: {str(e)}")

@router.post("/generate-summary")
async def generate_summary(request: SummaryRequest):
    """
    Generates a summary for the given publication using ChatNVIDIA.
    - Checks for an existing summary in `silver/publication_summary/`.
    - If not found, fetches extracted text from `silver/publications/`.
    - Generates a summary using ChatNVIDIA with instructions to be concise.
    - Saves or overwrites the summary in S3.
    """
    try:
        # Extract the base file name from the PDF link to derive paths
        base_file_name = request.pdf_link.split('/')[-1].replace('.pdf', '').replace(' ', '-').lower()
        summary_key = f"silver/publication_summary/{base_file_name}.txt"
        publication_key = f"silver/publications/{base_file_name}/{base_file_name}.txt"
        bucket_name = os.getenv("S3_BUCKET_NAME")

        # Step 1: Fetch the extracted publication text from `silver/publications/`
        publication_text = get_s3_file_content(bucket_name, publication_key)

        # Adjusted: Truncate the text to fit within 5,000 tokens (approximately 25,000 characters)
        truncated_text = publication_text[:25000]  # Approximation for 5,000 tokens

        # Initialize ChatNVIDIA client with the correct API key
        client = ChatNVIDIA(
            model="nvidia/llama-3.1-nemotron-51b-instruct",
            api_key=os.getenv("NVIDIA_API_KEY"),
            temperature=0.5,
            top_p=1,
            max_tokens=1024,
        )

        # Create the prompt for generating a summary
        prompt = (
            "Create a concise and clear summary for the following text, highlighting key insights and important points. "
            "Keep the summary short and focused on essential information: "
            f"{truncated_text}"
        )

        try:
            # Send the prompt to ChatNVIDIA API and stream the response to generate a summary
            summary_chunks = client.stream([{"role": "user", "content": prompt}])
            summary = "".join(chunk.content for chunk in summary_chunks)

            # Step 3: Overwrite the summary in S3 in the `silver/publication_summary/` path
            s3_client.put_object(Bucket=bucket_name, Key=summary_key, Body=summary.encode('utf-8'))

            return {"summary": summary, "message": "Summary generated and saved successfully!"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error generating summary: {str(e)}")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in summary generation: {str(e)}")
