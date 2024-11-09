# streamlit_pages/qa_interface.py
import requests
import streamlit as st
from utils import (
    init_session_state, fetch_or_create_notes, update_research_notes, save_notes_to_s3, 
    append_to_research_notes, clear_session_state, generate_report
)

def show_qa_interface(API_BASE_URL):
    """Displays the Q/A interface for the selected publication."""

    # Initialize session state keys
    init_session_state({
        "research_notes": "",
        "history": [],
        "index": False,
        "current_pdf_id": None,
        "fetched_notes": False,
        "message": "",
        "query_mode": "Full Document"
    })

    selected_pub = st.session_state.get("selected_pub")
    pdf_link = selected_pub.get("PDF_LINK")
    pub_id = str(selected_pub.get("ID"))
    selected_pdf_url = st.session_state.get("selected_pdf_url", "")
    title = selected_pub.get("TITLE", "Q/A Interface")

    st.title(f"Q/A Interface - {title}")

    if st.session_state["message"]:
        st.info(st.session_state["message"])
        st.session_state["message"] = ""

    if st.session_state["current_pdf_id"] != pub_id:
        st.session_state["current_pdf_id"] = pub_id
        st.session_state["index"] = False

    if not st.session_state["index"]:
        check_and_process_index(API_BASE_URL, pub_id, selected_pdf_url)

    if not st.session_state.get("fetched_notes", False):
        fetch_or_create_notes(API_BASE_URL, pdf_link)
        st.session_state["fetched_notes"] = True

    st.markdown(f"[📄 View Selected PDF]({selected_pdf_url})", unsafe_allow_html=True)

    col_back, col_reload = st.columns([1, 10])
    with col_back:
        if st.button("🔙 Back to Detail View"):
            clear_session_state()
            st.session_state["page"] = "detail_view"
            st.rerun()
    with col_reload:
        if st.button("Reload Q/A Interface"):
            reload_qa_interface(API_BASE_URL, selected_pdf_url, pub_id)

    st.markdown("## Research Notes")
    st.text_area("Research Notes", value=st.session_state.get("research_notes", ""), height=200, key="research_notes_input", on_change=update_research_notes)

    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if st.button("💾 Save Notes"):
            save_notes_to_s3(API_BASE_URL, pdf_link)
            st.session_state["message"] = "Research notes saved successfully!"
            st.rerun()
    with col2:
        if st.button("🔄 Refetch Notes"):
            fetch_or_create_notes(API_BASE_URL, pdf_link)
            st.session_state["message"] = "Research notes refetched successfully!"
            st.rerun()
    with col3:
        if st.button("❌ Clear Notes"):
            st.session_state["research_notes"] = ""
            st.session_state["message"] = "Research notes cleared!"
            st.rerun()

    query_mode = st.radio("Select Query Mode", options=["Full Document", "Research Notes"], key="query_mode")

    # New section for report generation
    # Replace the report generation section with this:
    if st.button("Generate Report"):
        if st.session_state['history']:
            report_data = generate_report(API_BASE_URL, pub_id, st.session_state['history'], query_mode)
            if report_data:
                st.session_state.report_data = report_data
                st.session_state.page = "report_page"
                st.rerun()
        else:
            st.warning("Please have a conversation before generating a report.")
    st.markdown(f"## Chat with the Assistant ({query_mode})")

    if st.session_state["index"]:
        chat_container = st.container()
        with chat_container:
            for i, message in enumerate(st.session_state['history']):
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])
                    if message["role"] == "assistant":
                        if st.button("Add to Research Notes", key=f"save_{message['role']}_{i}"):
                            append_to_research_notes(message["content"])
                            st.rerun()

        user_input = st.chat_input("Enter your query:")
        if user_input:
            with st.chat_message("user"):
                st.markdown(user_input)
            st.session_state['history'].append({"role": "user", "content": user_input})

            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                full_response = query_engine(user_input, API_BASE_URL, pub_id, query_mode)
                message_placeholder.markdown(full_response)

            st.session_state['history'].append({"role": "assistant", "content": full_response})
            st.rerun()

        if st.button("Clear Chat"):
            st.session_state['history'] = []
            st.rerun()

def check_and_process_index(API_BASE_URL, pub_id, selected_pdf_url):
    """Check if the index exists or process and create it if not."""
    with st.spinner("Checking if index already exists..."):
        try:
            response = requests.get(f"{API_BASE_URL}/rag/check-index", params={"pdf_id": pub_id})
            if response.status_code == 200 and response.json().get("index_exists"):
                st.session_state['index'] = True
                st.session_state['history'] = []
                st.success("Index already exists! You can start querying.")
            else:
                with st.spinner("Processing and indexing PDF..."):
                    response = requests.post(f"{API_BASE_URL}/rag/process-pdf", json={"pdf_link": selected_pdf_url, "pdf_id": pub_id})
                    if response.status_code == 200:
                        st.session_state['index'] = True
                        st.session_state['history'] = []
                        st.success("PDF processed and index created successfully!")
                    else:
                        st.error(f"Failed to process the PDF. Error: {response.status_code} - {response.json().get('detail', 'Unknown error')}")
                        return
        except Exception as e:
            st.error(f"Error during processing or index check: {str(e)}")
            return

def query_engine(query, API_BASE_URL, pub_id, query_mode):
    try:
        index_type = "pdf-index" if query_mode == "Full Document" else "research-notes"
        response = requests.post(f"{API_BASE_URL}/rag/query", json={"question": query, "pdf_id": pub_id, "index_type": index_type})
        if response.status_code == 200:
            return response.json().get("answer", "")
        elif response.status_code == 404 and index_type == "research-notes":
            return "Research notes index not found. Please save research notes first."
        else:
            return f"Error querying the assistant: {response.status_code} - {response.json().get('detail', 'Unknown error')}"
    except Exception as e:
        return f"Error querying the assistant: {str(e)}"

def reload_qa_interface(API_BASE_URL, selected_pdf_url, pub_id):
    """Reloads and reprocesses the Q/A interface for the given publication."""
    with st.spinner("Reprocessing and reindexing PDF..."):
        try:
            response = requests.post(f"{API_BASE_URL}/rag/reload-pdf", json={"pdf_link": selected_pdf_url, "pdf_id": pub_id})
            if response.status_code == 200:
                st.session_state['index'] = True
                st.session_state['history'] = []
                st.success("PDF reprocessed and index recreated successfully!")
            else:
                st.error(f"Failed to reload the Q/A Interface. Error: {response.status_code} - {response.json().get('detail', 'Unknown error')}")
                return
        except Exception as e:
            st.error(f"Error reloading the Q/A Interface: {str(e)}")
            return


def generate_report(API_BASE_URL, pub_id, conversation_history, query_mode):
    try:
        index_type = "pdf-index" if query_mode == "Full Document" else "research-notes"
        payload = {
            "conversation": conversation_history,
            "pdf_id": pub_id,
            "index_type": index_type,
            "research_notes": st.session_state.get("research_notes", "")  # Include current research notes
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