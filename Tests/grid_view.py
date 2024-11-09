import streamlit as st
from streamlit_pages.utils import fetch_publications, fetch_image_url
import os

def show_grid_view(API_BASE_URL):
    """Displays a grid view of the available publications."""
    publications = fetch_publications(API_BASE_URL)

    if publications:
        st.subheader("Explore Publications")
        st.markdown("Select a publication to view more details.")
        st.markdown("---")

        # Define the number of columns in the grid
        num_cols = 4  # Set to 4 columns per row for better alignment

        # Placeholder image path for publications without images
        placeholder_image_path = os.path.join(os.path.dirname(__file__), "no-image-placeholder.png")

        # Loop through publications and display them in a grid format
        for idx, pub in enumerate(publications):
            if idx % num_cols == 0:
                # Create a new row for every `num_cols` publications
                cols = st.columns(num_cols)

            # Get the column for the current publication
            col = cols[idx % num_cols]

            with col:
                # Extract the file key including the folder path
                file_key = "/".join(pub['cover_image_link'].split('/')[-3:]) if pub.get('cover_image_link') else None
                image_url = fetch_image_url(API_BASE_URL, file_key) if file_key else placeholder_image_path

                # Verify if the fetched image URL is None or not working
                if not image_url or image_url == "" or image_url == placeholder_image_path:
                    st.warning(f"Using placeholder for {pub['title']}. File key: {file_key}")
                    image_url = placeholder_image_path

                # Display the image using a clickable markdown link
                if image_url.startswith("http"):
                    # Remote image - create a clickable image using an anchor tag in Markdown
                    image_html = f"""
                    <a href="/?selected_pub_id={pub['id']}">
                        <img src="{image_url}" alt="{pub['title']}" style="width:150px; height:200px; border-radius: 8px; margin-bottom: 5px;">
                    </a>
                    """
                else:
                    # Local image - using Streamlit's image display
                    image_html = f"""
                    <a href="/?selected_pub_id={pub['id']}">
                        <img src="data:image/png;base64,{image_to_base64(image_url)}" alt="{pub['title']}" style="width:150px; height:200px; border-radius: 8px; margin-bottom: 5px;">
                    </a>
                    """

                # Display the clickable image
                col.markdown(image_html, unsafe_allow_html=True)

                # Display the publication title as a clickable button
                if col.button(pub['title'], key=f"btn_{pub['id']}"):
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
        selected_pub = next((pub for pub in publications if str(pub['id']) == selected_pub_id), None)
        if selected_pub:
            # Update session state for the selected publication
            st.session_state["selected_pub"] = selected_pub
            st.session_state["page"] = "detail_view"

            # Clear the query parameters to avoid repetition by setting an empty dictionary
            st.query_params.clear()
            
            # Rerun to go to the detailed view
            st.rerun()


def image_to_base64(image_path):
    """Converts an image file to a Base64 string."""
    import base64
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")
