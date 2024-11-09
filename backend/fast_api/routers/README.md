# Routers

The **routers** folder contains the various FastAPI routers that define specific endpoints for the Document Exploration Platform. Each router handles a distinct set of functionalities such as managing interactions with Snowflake, S3, NVIDIA’s summarization services, and Pinecone-based RAG model queries.

## Folder Structure

- **[`rag_router.py`](./rag_router.py)**: Router for indexing and querying documents using multi-modal Retrieval-Augmented Generation (RAG) and Pinecone.
- **[`s3_router.py`](./s3_router.py)**: Router for managing S3 interactions, including fetching images, PDFs, summaries, and saving research notes.
- **[`snowflake_router.py`](./snowflake_router.py)**: Router for interacting with Snowflake to fetch and manage publication metadata.
- **[`summarization_router.py`](./summarization_router.py)**: Router for generating summaries of publications using NVIDIA’s AI models.

## Overview of Each Router

1. **RAG Router** - [`rag_router.py`](./rag_router.py):  
   This router handles document indexing and querying using the multi-modal Retrieval-Augmented Generation (RAG) model. It leverages Pinecone as the vector database to store and retrieve document embeddings for efficient and accurate querying. Users can perform queries on full documents or research notes separately.

2. **S3 Router** - [`s3_router.py`](./s3_router.py):  
   The S3 router is responsible for managing interactions with AWS S3. It provides endpoints to fetch pre-signed URLs for publication images and PDFs, as well as endpoints to fetch and save research notes. It also handles fetching summaries stored in S3.

3. **Snowflake Router** - [`snowflake_router.py`](./snowflake_router.py):  
   The Snowflake router manages interactions with the Snowflake database. It includes endpoints for fetching publication metadata, such as titles, brief summaries, authors, image links, PDF links, and research notes. It interacts with the Snowflake table that stores publication data.

4. **Summarization Router** - [`summarization_router.py`](./summarization_router.py):  
   The Summarization router provides endpoints to generate summaries of publications using NVIDIA’s LLM models. It checks for existing summaries in S3 and, if not found, extracts the text from stored publications and generates a concise summary using NVIDIA’s AI services. The generated summaries are then saved back to S3 for future use.

## Integration with `fastapi_main.py`

These routers are included in the main FastAPI application through `fastapi_main.py`. Each router is assigned a prefix and tags, which organize the API documentation and separate the various functionalities within the platform. This modular approach allows for easy maintenance and scalability of the backend.

