#streamlit_pages/detail_view.py
import streamlit as st
import requests
from utils import fetch_image_url, fetch_pdf_url, fetch_summary

def show_detail_view(API_BASE_URL):
    """Displays detailed information of a selected publication."""
    if st.session_state.get("selected_pub") is not None:
        selected_pub = st.session_state["selected_pub"]

        # Add a button to go back to the list view at the top
        if st.button("🔙 Back to List"):
            st.session_state["selected_pub"] = None
            st.session_state["page"] = "grid_view"
            st.rerun()

        # Create two columns: one for the image and another for text details
        col1, col2 = st.columns([1, 2])  # Adjust the proportion as needed

        with col1:
            # Display the cover image if available
            if selected_pub.get('IMAGE_LINK'):
                file_key = "/".join(selected_pub['IMAGE_LINK'].split('/')[-3:])
                image_url = fetch_image_url(API_BASE_URL, file_key)

                if image_url:
                    st.image(image_url, caption=selected_pub['TITLE'], width=250)  # Slightly bigger image size

            # Fetch and display the pre-signed URL for downloading the PDF below the image
            if selected_pub.get('PDF_LINK'):
                pdf_key = "/".join(selected_pub['PDF_LINK'].split('/')[-3:])  # Extract the key from the link
                pdf_url = fetch_pdf_url(API_BASE_URL, pdf_key)  # Fetch the pre-signed URL for the PDF

                if pdf_url:
                    st.markdown(f"[📄 Download PDF]({pdf_url})", unsafe_allow_html=True)

        with col2:
            # Display publication details with proper formatting
            st.markdown(f"### {selected_pub['TITLE']}")  # Title as a heading
            st.write(f"**Author:** {selected_pub['AUTHOR']}")
            st.write(f"**Date:** {selected_pub['DATE']}")
            st.write(f"**Description:** {selected_pub['BRIEF_SUMMARY']}")

            # Display Created Date if available
            if selected_pub.get("CREATED_DATE"):
                st.write(f"**Created On:** {selected_pub['CREATED_DATE']}")

            if st.button("Take me to Q/A Interface"):
                if pdf_url and pdf_url.startswith(('http://', 'https://')):
                    st.session_state["selected_pdf_url"] = pdf_url
                    st.session_state["page"] = "qa_interface"
                    st.rerun()
                else:
                    st.error("Invalid or missing PDF URL. Please try refreshing the page or selecting the publication again.")

        st.markdown("---")

        # Add custom CSS to create a border
        st.markdown("""
        <style>
        .stColumn {
            border-right: 1px solid #e0e0e0;
            padding-right: 20px;
        }
        </style>
        """, unsafe_allow_html=True)

        # Summary and Research Notes side by side in a 2:1 ratio
        col_summary, col_notes = st.columns([2, 1])

        with col_summary:
            st.markdown('<div class="stColumn">', unsafe_allow_html=True)
            st.markdown("## Summary Section")
            if st.button("🔄 Refresh Summary", key="refresh_summary_button"):
                with st.spinner("Generating summary..."):
                    payload = {"pdf_link": selected_pub["PDF_LINK"]}
                    response = requests.post(f"{API_BASE_URL}/summarization/generate-summary", json=payload)
                    if response.status_code == 200:
                        new_summary = response.json().get("summary", "")
                        if new_summary:
                            st.success("Summary generated successfully!")
                            st.write(new_summary)
                        else:
                            st.warning("Summary generated but no content received.")
                    else:
                        st.error(f"Failed to generate the summary. Error: {response.status_code} - {response.json().get('detail', 'Unknown error')}")

            # Extract the base file name without the extension from the PDF link to form the summary key
            try:
                base_file_name = selected_pub["PDF_LINK"].split('/')[-1].replace('.pdf', '')
                if not base_file_name:
                    raise ValueError("Failed to extract folder name from the PDF link.")
                summary_key = f"silver/publication_summary/{base_file_name}.txt"
            except Exception as e:
                st.error(f"Error forming summary key: {str(e)}")
                return

            # Fetch and display the summary
            summary_content, summary_timestamp = fetch_summary(API_BASE_URL, summary_key)

            if summary_content == "generate":
                st.warning("Summary not found. Click 'Refresh' to generate one.")
            elif summary_content:
                st.write(f"*Last updated on: {summary_timestamp}*")
                st.write(summary_content)
            else:
                st.warning("Summary not available. Click 'Refresh' to generate one.")
            st.markdown('</div>', unsafe_allow_html=True)

        with col_notes:
            st.markdown("## Research Notes")
            display_research_notes(API_BASE_URL, selected_pub["PDF_LINK"])

    else:
        st.error("No publication selected.")

def display_research_notes(API_BASE_URL, pdf_link):
    """Fetch and display research notes from S3. Create an empty file if not found."""
    try:
        response = requests.get(f"{API_BASE_URL}/s3/fetch-research-notes", params={"pdf_link": pdf_link})
        if response.status_code == 200:
            notes_content = response.json().get("notes", "")
            if notes_content:
                st.write(notes_content)
            else:
                st.info("No research notes available. You can start by going to the Q/A Interface to take notes.")
        elif response.status_code == 404:
            st.info("No research notes available. You can start by going to the Q/A Interface to take notes.")
        else:
            st.error(f"Failed to fetch research notes. Error: {response.status_code} - {response.json().get('detail', 'Unknown error')}")

    except Exception as e:
        st.error(f"Error fetching research notes: {str(e)}")
