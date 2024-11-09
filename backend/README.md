# Backend

The **Backend** folder contains the core FastAPI service that powers the Document Exploration Platform. It includes multiple routers for handling various interactions, such as data storage, document processing, and AI-powered querying.

# Backend

This folder contains the backend components of the project, implemented using **FastAPI**. The backend includes various routers to interact with Snowflake, S3, NVIDIA models, and Pinecone. These routers manage document processing, summarization, indexing, and Q&A functionalities.

## Folder Structure

- **[fast_api](./fast_api/README.md)**: Main FastAPI application with routes for document exploration, summarization, research notes, and S3 interactions.
  - **[routers](./fast_api/routers/README.md)**: FastAPI routers for handling different functionalities:
    - **[rag_router.py](./fast_api/routers/rag_router.py)**: Router for indexing and querying documents using multi-modal RAG and Pinecone.
    - **[s3_router.py](./fast_api/routers/s3_router.py)**: Router for managing S3 interactions such as fetching images, PDFs, summaries, and saving research notes.
    - **[snowflake_router.py](./fast_api/routers/snowflake_router.py)**: Router for interacting with Snowflake to fetch publication data.
    - **[summarization_router.py](./fast_api/routers/summarization_router.py)**: Router for generating summaries using NVIDIA’s AI models.
  - **[fastapi_main.py](./fast_api/fastapi_main.py)**: Main entry point for the FastAPI server that includes all routers.

- **[utils](./utils/README.md)**: Utility functions for processing PDFs, managing S3 interactions, and handling various helper operations.
  - **[helper_functions.py](./utils/helper_functions.py)**: Contains helper functions for environment management, image processing, cache clearing, and API interactions.
  - **[pdf_processor.py](./utils/pdf_processor.py)**: Handles the extraction of text, tables, and images from PDF documents.


## Usage

1. **Start the FastAPI Server**:  
   If using Docker, the backend will be started automatically using Docker Compose. To run it manually, navigate to the `backend` directory and use the following command:  
   ```bash
   uvicorn fast_api.fastapi_main:app --host 0.0.0.0 --port 8000
   ```

2. **Access API Documentation**:
The OpenAPI documentation for FastAPI can be accessed at http://localhost:8000/docs.

3. **Environment Variables**:
Ensure that the .env file is correctly set up with credentials for AWS, Snowflake, Pinecone, and NVIDIA.

## License

This project is licensed under the MIT License. For more details, please refer to the [LICENSE](/LICENSE) file.