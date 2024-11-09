# Airflow Docker Pipeline

This folder contains the necessary configurations, scripts, and Docker setup to automate the data ingestion, processing, and summarization of publications using Apache Airflow. The pipelines scrape publications, upload files to AWS S3, and set up a Snowflake database for storing publication metadata.

## Folder Structure

📂 airflow_docker_pipelines  
├── Dockerfile                      # Dockerfile for building the Airflow container image  
├── docker-compose.yml             # Docker Compose configuration for running Airflow  
├── pdf_extraction_dag.py          # DAG script for extracting text from PDFs and uploading to S3  
├── scrape_cfa_publications_dag.py # DAG script for scraping CFA publications and storing metadata in S3  
├── snowflake_setup_dag.py         # DAG script for setting up Snowflake infrastructure  
├── snowflake_load_dag.py          # DAG script for loading publication data into Snowflake from S3  

## DAG Scripts Overview

### 1. `pdf_extraction_dag.py`
- **Purpose**: Extracts text content from PDFs stored in S3 using the PyMuPDF library.
- **Functionality**: 
  - Lists PDFs stored in the S3 bucket.
  - Extracts text using PyMuPDF.
  - Saves extracted text as `.txt` files in S3 under a specific folder structure.
  
### 2. `scrape_cfa_publications_dag.py`
- **Purpose**: Scrapes CFA Institute Research Foundation Publications and stores publication metadata and files in S3.
- **Functionality**: 
  - Uses Selenium to scrape the CFA publications' website.
  - Downloads publication cover images and PDF files.
  - Uploads files to an S3 bucket and stores metadata in a CSV file.

### 3. `snowflake_setup_dag.py`
- **Purpose**: Sets up Snowflake infrastructure including the warehouse, database, schema, and table for storing publication metadata.
- **Functionality**: 
  - Establishes a connection with Snowflake.
  - Creates the necessary warehouse, database, schema, and table if they do not already exist.

### 4. `snowflake_load_dag.py`
- **Purpose**: Loads publication metadata from the CSV stored in S3 into the Snowflake table.
- **Functionality**: 
  - Reads the publication CSV file from S3.
  - Loads data into Snowflake using a merge operation to update or insert publication records.

## Docker Setup

### Dockerfile
The Dockerfile is used to build an Airflow Docker image with all the required dependencies.

**Key Steps in the Dockerfile**:
- Sets up a base Python environment.
- Installs Apache Airflow and other required libraries.
- Copies the DAGs and scripts into the container.

### Docker Compose

The `docker-compose.yml` file sets up the Airflow environment using the Docker image. It defines the services needed for Airflow, including the web server, scheduler, and PostgreSQL database.

**Key Environment Variables**:
- AWS Access Credentials: Required to access and upload files to S3.
- Snowflake Credentials: Required to set up and load data into the Snowflake database.
- Airflow User Credentials: Used to create the initial Airflow admin user.

## Usage

### Step-by-Step Instructions

1. **Build the Docker Image**:
```bash
   docker build -t airflow-scrape:latest .
```

2. **Initialize Airflow**:
```bash
   AIRFLOW_IMAGE_NAME=airflow-scrape:latest AIRFLOW_UID=0 _AIRFLOW_WWW_USER_USERNAME=admin _AIRFLOW_WWW_USER_PASSWORD=admin123 AWS_ACCESS_KEY_ID='your-access-key-id' AWS_SECRET_ACCESS_KEY='your-secret-access-key' AWS_REGION='your-aws-region' S3_BUCKET_NAME='your-s3-bucket-name' SNOWFLAKE_ACCOUNT='your-snowflake-account' SNOWFLAKE_USER='your-snowflake-user' SNOWFLAKE_PASSWORD='your-snowflake-password' SNOWFLAKE_ROLE='your-snowflake-role' docker-compose up airflow-init
```

3. **Start Airflow Services**:
```bash
   AIRFLOW_IMAGE_NAME=airflow-scrape:latest AIRFLOW_UID=0 _AIRFLOW_WWW_USER_USERNAME=admin _AIRFLOW_WWW_USER_PASSWORD=admin123 AWS_ACCESS_KEY_ID='your-access-key-id' AWS_SECRET_ACCESS_KEY='your-secret-access-key' AWS_REGION='your-aws-region' S3_BUCKET_NAME='your-s3-bucket-name' SNOWFLAKE_ACCOUNT='your-snowflake-account' SNOWFLAKE_USER='your-snowflake-user' SNOWFLAKE_PASSWORD='your-snowflake-password' SNOWFLAKE_ROLE='your-snowflake-role' docker-compose up -d
```

4. **Login to Airflow and Trigger DAGs in the Correct Sequence**:
   - **Login to Airflow**:  
     - Access the Airflow web server at `http://localhost:8080`.
     - Login with the default credentials:
       - Username: `admin`
       - Password: `admin123`

   - **Trigger the DAGs** in the following sequence using the Airflow UI or CLI:
     1. **Scrape CFA Publications**:
        - Use the Airflow UI to trigger the `scrape_cfa_publications_dag`.
        - Alternatively, run the following command:
          ```bash
          docker-compose run airflow-cli dags trigger scrape_cfa_publications_dag
          ```

     2. **Setup Snowflake**:
        - Use the Airflow UI to trigger the `snowflake_setup_dag`.
        - Alternatively, run the following command:
          ```bash
          docker-compose run airflow-cli dags trigger snowflake_setup_dag
          ```

     3. **Load Data into Snowflake**:
        - Use the Airflow UI to trigger the `snowflake_load_dag`.
        - Alternatively, run the following command:
          ```bash
          docker-compose run airflow-cli dags trigger snowflake_load_dag
          ```

     4. **Extract PDF Summarization**:
        - Use the Airflow UI to trigger the `pdf_extraction_dag`.
        - Alternatively, run the following command:
          ```bash
          docker-compose run airflow-cli dags trigger pdf_extraction_dag
          ```

### Notes:
- Ensure that the Airflow web server is accessible at `http://localhost:8080` to monitor and manage DAG runs.
- The Snowflake database setup, data load, and PDF processing DAGs can be managed via the Airflow UI if needed.

## Troubleshooting

### Common Issues and Solutions

1. **Airflow Initialization Issues**:
   - **Issue**: Airflow services fail to initialize or there are permission errors.
   - **Solution**: Ensure that the `AIRFLOW_UID` is set to `0` for root-level permissions in Docker, and all necessary environment variables are correctly defined. You can run:
     ```bash
     AIRFLOW_UID=0 docker-compose up airflow-init
     ```

2. **Missing or Invalid Credentials**:
   - **Issue**: AWS or Snowflake connections fail due to missing or invalid credentials.
   - **Solution**: Verify that the `.env` file contains the correct keys and secrets for AWS, Snowflake, NVIDIA, and Pinecone. Additionally, ensure that the S3 bucket name is correct and accessible.

3. **DAG Not Triggering Properly**:
   - **Issue**: DAGs fail to trigger or are stuck in the “Queued” state.
   - **Solution**: Ensure that all necessary services are running using `docker-compose ps`. Check the Airflow UI (`http://localhost:8080`) for errors and logs related to the DAG. If needed, try restarting the affected services.

4. **Snowflake Connectivity Errors**:
   - **Issue**: Snowflake-related operations fail due to connectivity issues.
   - **Solution**: Check that your Snowflake account, user, password, and role in the `.env` file are correct. Ensure that Snowflake is accessible from your network, and update firewall rules if necessary.

5. **PDF Extraction Issues**:
   - **Issue**: Errors in extracting text from PDF files or uploading them to S3.
   - **Solution**: Ensure that the PDF files are not corrupted and are properly formatted. Verify that the S3 bucket permissions allow read/write access for the provided AWS credentials.


## License

This project is licensed under the MIT License. For more details, please refer to the [LICENSE](/LICENSE) file.