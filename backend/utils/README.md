# Utils

The **utils** folder contains various utility functions and scripts that support the core functionalities of the backend service. These utilities include helper functions for environment management, PDF processing, image handling, and caching operations.

## Folder Structure

- **[`helper_functions.py`](./helper_functions.py)**: Contains various helper functions for setting environment variables, processing images, clearing cache directories, and managing API interactions.
- **[`pdf_processor.py`](./pdf_processor.py)**: Handles the extraction of text, tables, and images from PDF documents. It includes functions for parsing and organizing different types of document content.

## Overview of Each Utility

1. **Helper Functions** - [`helper_functions.py`](./helper_functions.py):  
   This file contains a collection of helper functions used throughout the backend service. Key functionalities include:
   - **Environment Management**: Functions to set up environment variables for NVIDIA API keys and other services.
   - **Image Processing**: Functions to handle image conversions, descriptions, and checks for graphs or charts.
   - **Cache Management**: Functions to clear and manage the cache directory to ensure efficient storage usage.
   - **API Interactions**: Functions to interact with NVIDIA’s AI models for generating image descriptions and processing graphs.

2. **PDF Processor** - [`pdf_processor.py`](./pdf_processor.py):  
   This utility handles the extraction and processing of PDF content. It includes:
   - **Text Extraction**: Functions to extract text blocks and group them into meaningful sections.
   - **Table and Image Parsing**: Functions to identify and extract tables and images from PDF pages, generate descriptions, and store them appropriately for indexing.
   - **Metadata Handling**: Functions to create metadata for extracted text, tables, and images, which are then used to create document objects for indexing.

## Integration with FastAPI

The utilities in this folder are essential for the backend’s core operations. They are used by the various routers to process PDF documents, handle images, interact with APIs, and manage cached data. The utilities are designed to be modular and reusable across different parts of the backend service.

## License

This project is licensed under the MIT License. For more details, please refer to the [LICENSE](/LICENSE) file.