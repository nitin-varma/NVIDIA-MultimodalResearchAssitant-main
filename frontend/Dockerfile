# Dockerfile for frontend (Streamlit)
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /streamlit-app

# Copy the requirements file to the container
COPY requirements.txt /streamlit-app/

# Install the required packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . /streamlit-app

# Expose the port that Streamlit runs on
EXPOSE 8501

# Define the command to run Streamlit when the container starts
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
