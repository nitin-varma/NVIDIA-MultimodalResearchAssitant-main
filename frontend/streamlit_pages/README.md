# Streamlit Pages

The **streamlit_pages** folder contains the key pages for the Streamlit application. These pages are responsible for presenting different views and functionalities to the user, such as browsing publications, viewing detailed information, and interacting with a Q/A interface.

## Folder Structure

- **[`grid_view.py`](./grid_view.py)**: Displays a grid view of all available publications. Each publication is represented by an image, which users can click to view more details.
- **[`detail_view.py`](./detail_view.py)**: Shows detailed information for the selected publication, including the title, author, date published, summary, and research notes. This page also includes options to refresh the summary and navigate to the Q/A interface.
- **[`qa_interface.py`](./qa_interface.py)**: Provides a Question/Answer interface for interacting with the selected document using a multi-modal RAG model. Users can query the document, view and save research notes, and reload the Q/A interface if needed.

## Pages Overview

### **grid_view.py**

The `grid_view.py` file handles the display of all available publications in a grid format. It uses the following features:
- **Grid Display**: Shows publications as clickable images in a grid format. When a user clicks on a publication, they are redirected to the **Detail View**.
- **Navigation**: Keeps track of the selected publication and navigates users to the appropriate page based on their selection.

### **detail_view.py**

The `detail_view.py` file is responsible for displaying detailed information about the selected publication. It includes the following features:
- **Metadata Display**: Shows publication details like the title, author, date, and brief summary.
- **Summary Generation**: Fetches or generates a summary using the backend’s NVIDIA-based AI models. Users can refresh the summary if needed.
- **Research Notes**: Allows users to view and add research notes related to the publication.
- **Navigation to Q/A Interface**: Provides a button to navigate to the Q/A interface for more in-depth interaction with the document.

### **qa_interface.py**

The `qa_interface.py` file handles the interaction between the user and the selected document through a Q/A system. It includes the following features:
- **Query Document**: Allows users to ask questions about the document, using the multi-modal RAG (Retrieval-Augmented Generation) model.
- **Research Notes Management**: Provides options to save the generated responses as research notes.
- **Separate Query Modes**: Users can choose to query either the full document or the indexed research notes for more precise results.

## Usage

1. **Grid View**: Users start by exploring the available publications in the grid view. Each publication is represented by a clickable image.
2. **Detail View**: After selecting a publication, users are redirected to the detail view where they can see detailed metadata, generate summaries, and view research notes.
3. **Q/A Interface**: From the detail view, users can navigate to the Q/A interface, where they can ask questions and interact with the selected document.

This folder structure ensures a clean separation of functionalities, making it easier to maintain and expand the Streamlit application as needed.

## License

This project is licensed under the MIT License. For more details, please refer to the [LICENSE](/LICENSE) file.