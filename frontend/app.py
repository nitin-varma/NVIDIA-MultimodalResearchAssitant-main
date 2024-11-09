# app.py
import streamlit as st
from streamlit_pages import grid_view, detail_view, qa_interface, report_page
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# FastAPI URL (change it if you deploy it to an online server)
FASTAPI_URL = os.getenv("FASTAPI_URL")

# Set Streamlit page configuration to wide mode
st.set_page_config(layout="wide")

def main():
    # Initialize session state for navigation
    if "page" not in st.session_state:
        st.session_state["page"] = "grid_view"
        st.rerun() 

    # Only show the title on the grid view page
    if st.session_state["page"] == "grid_view":
        st.title("📚 Document Exploration Platform")

    # Navigation between pages based on session state
    if st.session_state["page"] == "grid_view":
        grid_view.show_grid_view(FASTAPI_URL)
    elif st.session_state["page"] == "detail_view":
        detail_view.show_detail_view(FASTAPI_URL)
    elif st.session_state["page"] == "qa_interface":
        qa_interface.show_qa_interface(FASTAPI_URL)
    elif st.session_state["page"] == "report_page":
        report_page.show_report_page(FASTAPI_URL)

if __name__ == "__main__":
    main()