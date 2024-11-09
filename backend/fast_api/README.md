# fast_api

The **fast_api** folder contains the main FastAPI application that serves as the core backend service for the Document Exploration Platform. This application is responsible for handling API requests, processing documents, and interacting with external services such as AWS S3, Snowflake, Pinecone, and NVIDIA's AI models.

## Folder Structure

- **[`fastapi_main.py`](./fastapi_main.py)**: The main entry point for the FastAPI server, which includes all the required routers and configurations.
- **[`routers/`](./routers/README.md)**: Contains all the FastAPI routers that define specific functionalities for interacting with different services:
  - **[`rag_router.py`](./routers/rag_router.py)**: Router for indexing and querying documents using multi-modal Retrieval-Augmented Generation (RAG) and Pinecone.
  - **[`s3_router.py`](./routers/s3_router.py)**: Router for managing S3 interactions such as fetching images, PDFs, summaries, and saving research notes.
  - **[`snowflake_router.py`](./routers/snowflake_router.py)**: Router for interacting with Snowflake to fetch publication data.
  - **[`summarization_router.py`](./routers/summarization_router.py)**: Router for generating summaries using NVIDIA’s AI models.

## Overview of `fastapi_main.py`

The `fastapi_main.py` file acts as the main entry point for the FastAPI server. It configures the application, sets up CORS (Cross-Origin Resource Sharing), loads environment variables, and includes different routers that define the API's functionality.

### Key Components

1. **CORS Middleware**:  
   The application sets up CORS middleware to allow requests from all origins (`origins = ["*"]`). This is useful when the frontend is hosted separately or accessed from different domains.

2. **Environment Variables**:  
   Environment variables are loaded using `dotenv` to securely manage sensitive data such as API keys and access credentials. This includes credentials for AWS S3, Snowflake, Pinecone, and NVIDIA's services.

3. **Routers**:  
   The application includes several routers that define the core functionalities of the API:
   - **Snowflake Router** ([`snowflake_router`](./routers/snowflake_router.py)): Manages interactions with the Snowflake database for storing and fetching publication metadata.
   - **S3 Router** ([`s3_router`](./routers/s3_router.py)): Handles interactions with AWS S3 for fetching images, PDFs, and summaries, and for saving research notes.
   - **Summarization Router** ([`summarization_router`](./routers/summarization_router.py)): Provides endpoints for generating summaries of publications using NVIDIA’s AI models.
   - **RAG Router** ([`rag_router`](./routers/rag_router.py)): Facilitates document indexing and querying using the multi-modal Retrieval-Augmented Generation (RAG) model with Pinecone for vector storage.

4. **Root Endpoint**:  
   A basic root endpoint (`"/"`) is defined to confirm that the server is running. When accessed, it returns a simple JSON message: `{"message": "Welcome to the Document Exploration API"}`.

5. **App Configuration**:  
   The application is defined using the `FastAPI` class and is given a title, description, and version. The routers are included in the main application to enable their respective functionalities.

This file acts as the central hub for the FastAPI server, integrating all necessary routers and configurations to provide a cohesive backend service for document exploration, summarization, and querying.

## License

This project is licensed under the MIT License. For more details, please refer to the [LICENSE](/LICENSE) file.