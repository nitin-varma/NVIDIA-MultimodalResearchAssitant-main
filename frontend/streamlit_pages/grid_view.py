#streamlit_pages/grid_view.py
import streamlit as st
from utils import fetch_publications, fetch_image_url
import os

def show_grid_view(API_BASE_URL):
    """Displays a grid view of the available publications."""
    # Fetch the list of publications from the server
    publications = fetch_publications(API_BASE_URL)

    if publications:
        st.subheader("Explore Publications")
        st.markdown("Select a publication to view more details.")
        st.markdown("---")

        # Define the number of columns in the grid
        num_cols = 5  # Set to 5 columns per row for better alignment

        # Placeholder image path for publications without images
        placeholder_image_path = os.path.join("no-image-placeholder.png")

        # Loop through publications and display them in a grid format
        for idx, pub in enumerate(publications):
            if idx % num_cols == 0:
                # Create a new row for every `num_cols` publications
                cols = st.columns(num_cols, gap="small")  # Reduce the gap between columns

            # Get the column for the current publication
            col = cols[idx % num_cols]

            with col:
                # Extract the file key including the folder path
                file_key = "/".join(pub['IMAGE_LINK'].split('/')[-3:]) if pub.get('IMAGE_LINK') else None
                image_url = fetch_image_url(API_BASE_URL, file_key) if file_key else placeholder_image_path

                # Verify if the fetched image URL is None or not working
                if not image_url or image_url == placeholder_image_path:
                    image_url = placeholder_image_path

                # Display the image with a fixed size and make it clickable
                if image_url == placeholder_image_path:
                    # Display placeholder image if actual image not available
                    col.image(image_url, use_column_width=False, width=150, caption=pub['TITLE'])
                else:
                    # Create a clickable image using an anchor tag in Markdown
                    image_html = f"""
                    <a href="/?selected_pub_id={pub['ID']}">
                        <img src="{image_url}" alt="{pub['TITLE']}" style="width:140px; height:190px; border-radius: 6px; margin-bottom: 5px;">
                    </a>
                    """
                    # Display the clickable image using Markdown
                    col.markdown(image_html, unsafe_allow_html=True)

                # Display the publication title as a clickable button with adjusted width
                button_style = f"""
                <style>
                    .stButton>button {{
                        width: 140px;
                        height: auto;
                        white-space: normal;
                        text-align: center;
                        padding: 5px;
                        font-size: 12px;
                        word-wrap: break-word;
                        line-height: 1.2;
                    }}
                </style>
                """
                col.markdown(button_style, unsafe_allow_html=True)
                if col.button(pub['TITLE'], key=f"btn_{pub['ID']}"):
                    # When the button is clicked, update the session state and navigate to the detail view
                    st.session_state["selected_pub"] = pub
                    st.session_state["page"] = "detail_view"
                    st.rerun()

        st.markdown("---")

    # Check URL parameters for selected publication using st.query_params
    query_params = st.query_params  # Access query parameters using st.query_params dictionary-like interface
    selected_pub_id = query_params.get('selected_pub_id', [None])[0]

    if selected_pub_id:
        # Validate the selected publication based on the ID in the query parameters
        selected_pub = next((pub for pub in publications if str(pub['ID']) == selected_pub_id), None)
        if selected_pub:
            # Update session state for the selected publication
            st.session_state["selected_pub"] = selected_pub
            st.session_state["page"] = "detail_view"

            # Clear the query parameters to avoid repetition by setting an empty dictionary
            st.query_params.clear()
            
            # Rerun to go to the detailed view
            st.rerun()

