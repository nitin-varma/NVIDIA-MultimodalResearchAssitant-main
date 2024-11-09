# In streamlit_pages/report_page.py

import streamlit as st

def show_report_page(API_BASE_URL):
    st.title("Generated Report")

    if "report_data" not in st.session_state:
        st.error("No report data available. Please generate a report first.")
        return

    report_data = st.session_state.report_data

    st.header("Summary")
    st.write(report_data["summary"])

    st.header("Explanation")
    st.write(report_data["explanation"])

    st.header("Research Notes")
    if report_data["research_notes"]:
            st.markdown(report_data["research_notes"])
    else:
            st.info("No research notes available.")
    

    st.header("Conversation")
    for message in report_data["conversation"]:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    if st.button("Back to Q/A Interface"):
        st.session_state.page = "qa_interface"
        st.rerun()