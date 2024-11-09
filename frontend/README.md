# Frontend

The **frontend** folder contains the Streamlit application that serves as the user interface for the Document Exploration Platform. It includes multiple pages for exploring publications, viewing document details, and interacting with the Q/A interface. The application is designed to provide a user-friendly experience with dynamic functionalities for document browsing, summarization, and querying.

## Folder Structure

- **[`app.py`](./app.py)**: The main entry point for the Streamlit application. It initializes the environment, manages page navigation using session state, and handles the overall layout of the app. It includes a `main` function that switches between pages based on the current state (`grid_view`, `detail_view`, and `qa_interface`).
- **[`streamlit_pages`](./streamlit_pages/README.md)**: Contains individual pages for different functionalities within the Streamlit app.
  - **[`grid_view.py`](./streamlit_pages/grid_view.py)**: Displays a grid of available publications with clickable images for easy navigation.
  - **[`detail_view.py`](./streamlit_pages/detail_view.py)**: Shows detailed information about selected publications, including summaries, research notes, and links to download PDFs.
  - **[`qa_interface.py`](./streamlit_pages/qa_interface.py)**: Provides a Q/A interface for querying documents using the multi-modal RAG model and saving notes.
- **[`utils.py`](./utils.py)**: Contains utility functions to interact with the backend API, handle session state, fetch images, summaries, research notes, and manage the Q/A interface. It includes functions for:
  - Fetching and processing publication data, images, and summaries from the backend.
  - Managing session states and research notes.
  - Handling the interaction between Streamlit components and the backend services.
- **[`Dockerfile`](./Dockerfile)**: Dockerfile for containerizing the Streamlit application.
- **[`requirements.txt`](./requirements.txt)**: Lists the Python dependencies required to run the Streamlit app.
- **[`no-image-placeholder.png`](./no-image-placeholder.png)**: A placeholder image used when a publication does not have an associated cover image.

## Application Overview

### **app.py**
The `app.py` file serves as the main entry point for the Streamlit application. It is responsible for initializing environment variables, configuring page layout, and managing navigation between different pages. The file includes three main views:
- **Grid View**: Displays publications in a grid format with clickable covers for easy navigation.
- **Detail View**: Provides detailed information for selected publications, including metadata, generated summaries, and research notes.
- **Q/A Interface**: Allows users to ask questions about documents using a multi-modal RAG model. Users can also save the generated answers as research notes.

### **utils.py**
The `utils.py` file contains essential utility functions that facilitate interaction between the Streamlit app and the backend. Key functionalities include:
- **Data Fetching**: Functions like `fetch_publications`, `fetch_image_url`, `fetch_pdf_url`, and `fetch_summary` allow the app to retrieve publication data, images, PDFs, and summaries from the backend API.
- **Session State Management**: Functions such as `init_session_state`, `update_research_notes`, and `clear_session_state` manage the Streamlit session state for smooth navigation and state preservation.
- **Research Notes Handling**: Includes functions like `fetch_or_create_notes`, `save_notes_to_s3`, and `append_to_research_notes` to help users save and manage research notes for each publication.

## Integration with Backend

The frontend communicates with the backend’s FastAPI service to fetch and update data. API requests are made for fetching publications, summaries, research notes, and interacting with the RAG model for question-answering. The `utils.py` file in the frontend handles these API calls and manages session state for the user.

## Usage

1. **Start the Streamlit Application**:  
   If using Docker, the frontend will be started automatically using Docker Compose. To run it manually, navigate to the `frontend` directory and use the following command:  
   ```bash
   streamlit run app.py 
   ```
2. **Access the Application**:
    Once started, you can access the Streamlit application at http://localhost:8501.

3. **Set Up Environment Variables**:
    Ensure that the FASTAPI_URL environment variable is set correctly in the .env file or in your terminal. This URL should point to the running FastAPI server, which is typically set to http://localhost:8000 if running locally.
    ```bash
    FASTAPI_URL='http://localhost:8000'
    ```
4. **Interacting with the Application**:
    Use the grid view to explore available publications. Select a publication to view its details, generate summaries, interact with the Q/A interface, and save research notes.

## License

This project is licensed under the MIT License. For more details, please refer to the [LICENSE](/LICENSE) file.