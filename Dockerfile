# Base image
FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV AIRFLOW_HOME /airflow

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    openssh-client \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create airflow directory and copy files
RUN mkdir -p ${AIRFLOW_HOME}/dags
WORKDIR ${AIRFLOW_HOME}

# Copy project files
COPY data_pipeline/orchestration/dags/ ${AIRFLOW_HOME}/dags/
COPY data_pipeline/ ${AIRFLOW_HOME}/data_pipeline/

# Initialize Airflow
RUN airflow db init

# Expose ports
EXPOSE 8080

# Entrypoint
ENTRYPOINT ["airflow"]
CMD ["webserver"]