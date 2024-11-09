#utils.py
import requests
import streamlit as st
from datetime import datetime
import pytz


def fetch_publications(API_BASE_URL):
    """Fetches a list of publications from the FastAPI server."""
    try:
        response = requests.get(f"{API_BASE_URL}/snowflake/publications")
        if response.status_code == 200:
            return response.json()
        else:
            st.error("Failed to fetch publications. Please try again later.")
            return []
    except Exception as e:
        st.error(f"Error fetching publications: {str(e)}")
        return []

def fetch_image_url(API_BASE_URL, file_key):
    """Fetches a pre-signed URL for an image from the S3 bucket using FastAPI."""
    placeholder_image_path = "no-image-placeholder.png"

    if file_key and "https://" not in file_key:
        try:
            response = requests.get(f"{API_BASE_URL}/s3/fetch-image/{file_key}")
            if response.status_code == 200:
                return response.json().get("image_url", placeholder_image_path)
            return placeholder_image_path
        except Exception:
            return placeholder_image_path
    else:
        return placeholder_image_path

def fetch_pdf_url(API_BASE_URL, file_key):
    """Fetches a pre-signed URL for a PDF from the S3 bucket using FastAPI."""
    try:
        response = requests.get(f"{API_BASE_URL}/s3/fetch-pdf/{file_key}")
        if response.status_code == 200:
            return response.json().get("pdf_url")
        return None
    except Exception as e:
        st.error(f"Error fetching PDF URL: {str(e)}")
        return None

def fetch_summary(API_BASE_URL, summary_key):
    """Fetches the summary from the S3 bucket using a pre-signed URL."""
    try:
        # Request to the backend to fetch the pre-signed URL and last modified time for the summary file
        response = requests.get(f"{API_BASE_URL}/s3/fetch-summary/{summary_key}")
        
        if response.status_code == 200:
            # Extract the pre-signed URL and last modified time from the backend response
            summary_url = response.json().get("summary_url")
            last_modified = response.json().get("last_modified", None)

            if summary_url:
                # Fetch the actual content of the summary using the pre-signed URL
                summary_response = requests.get(summary_url)
                
                if summary_response.status_code == 200:
                    # Convert the response content to text, assuming it's a plain text summary
                    summary_content = summary_response.text
                    
                    # If there is a last modified time, convert it to the target timezone
                    if last_modified:
                        # Parse the UTC time
                        utc_time = datetime.strptime(last_modified, "%Y-%m-%dT%H:%M:%S.%fZ")
                        # Convert to target timezone (e.g., America/New_York for UTC-04:00)
                        target_timezone = pytz.timezone("America/New_York")  # Change to your desired timezone
                        last_modified_local = utc_time.replace(tzinfo=pytz.utc).astimezone(target_timezone)
                        # Format the local time
                        last_modified = last_modified_local.strftime("%B %d, %Y, %H:%M:%S %p (%Z)")
                    
                    return summary_content, last_modified
                else:
                    return None, None  # Return None without logging error messages
            else:
                return None, None  # Return None if the pre-signed URL is not found
        elif response.status_code == 404:
            # If a 404 error is returned, the summary file does not exist
            return "generate", None  # Indicate that a new summary needs to be generated
        else:
            return None, None  # Return None without logging error messages
    except requests.exceptions.RequestException as e:
        return None, None  # Return None without logging error messages
    except Exception as e:
        return None, None  # Return None without logging error messages


def init_session_state(keys_defaults):
    """Initializes session state keys if not present."""
    for key, default in keys_defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default

def fetch_or_create_notes(API_BASE_URL, pdf_link):
    """Fetch research notes if they exist or create an empty file initially."""
    try:
        response = requests.get(f"{API_BASE_URL}/s3/fetch-research-notes", params={"pdf_link": pdf_link})
        if response.status_code == 200:
            notes_content = response.json().get("notes", "")
            st.session_state["research_notes"] = notes_content
            if not notes_content:
                st.info("No research notes available. You can start taking notes in the Q/A Interface.")
        elif response.status_code == 404:
            st.session_state["research_notes"] = ""
            st.info("No research notes found. You can start taking notes in the Q/A Interface.")
        else:
            response.raise_for_status()
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching research notes: {str(e)}")

def update_research_notes():
    """Update research notes in session state when edited."""
    st.session_state["research_notes"] = st.session_state["research_notes_input"]

def save_notes_to_s3(API_BASE_URL, pdf_link):
    """Save research notes to S3 and create or update an index in Pinecone."""
    try:
        pub_id = st.session_state.get("current_pdf_id", "")
        payload = {
            "pdf_link": pdf_link,
            "notes": st.session_state["research_notes"],
            "pdf_id": pub_id
        }
        response = requests.post(f"{API_BASE_URL}/s3/save-research-notes", json=payload)
        if response.status_code == 200:
            st.success("Research notes saved and indexed successfully!")
        else:
            st.error(f"Failed to save research notes to S3. Error: {response.status_code} - {response.json().get('detail', 'Unknown error')}")
    except Exception as e:
        st.error(f"Error saving research notes: {str(e)}")

def append_to_research_notes(content):
    """Append assistant's response to the research notes."""
    st.session_state["research_notes"] += f"\n\n{content}"

def clear_session_state(keys_to_clear=None):
    """Clears specific session state variables."""
    if keys_to_clear is None:
        keys_to_clear = ["message", "index", "history", "research_notes", "current_pdf_id", "fetched_notes"]
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]

def generate_report(API_BASE_URL, pub_id, conversation_history, query_mode):
    try:
        index_type = "pdf-index" if query_mode == "Full Document" else "research-notes"
        payload = {
            "conversation": conversation_history,
            "pdf_id": pub_id,
            "index_type": index_type
        }
        response = requests.post(f"{API_BASE_URL}/rag/generate-report", json=payload)
        if response.status_code == 200:
            return response.json().get("report", {})
        else:
            st.error(f"Error generating report: {response.status_code} - {response.json().get('detail', 'Unknown error')}")
            return None
    except Exception as e:
        st.error(f"Error generating report: {str(e)}")
        return None