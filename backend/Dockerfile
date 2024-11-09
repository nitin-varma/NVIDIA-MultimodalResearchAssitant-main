# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /fastapi-app

# Copy requirements.txt first to leverage Docker cache
COPY requirements.txt /fastapi-app/

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . /fastapi-app

# Expose the port FastAPI runs on
EXPOSE 8000

# Command to run the FastAPI application with uvicorn
CMD ["uvicorn", "fast_api.fastapi_main:app", "--host", "0.0.0.0", "--port", "8000"]
