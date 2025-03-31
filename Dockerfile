## Dockerfile (vous pouvez adapter à votre façon)
# Build stage
FROM python:3.9-slim as builder

# Install system dependencies for build
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    wget \
    openjdk-11-jdk \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
WORKDIR /app
COPY requirements.txt .
RUN pip install --user -r requirements.txt

# Download Spark (for local mode)
RUN wget https://archive.apache.org/dist/spark/spark-3.3.1/spark-3.3.1-bin-hadoop3.tgz && \
    tar -xzf spark-3.3.1-bin-hadoop3.tgz && \
    mv spark-3.3.1-bin-hadoop3 /opt/spark && \
    rm spark-3.3.1-bin-hadoop3.tgz

# Runtime stage
FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    AIRFLOW_HOME=/airflow \
    SPARK_HOME=/opt/spark \
    PATH=/root/.local/bin:$PATH \
    JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64

# Install runtime dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libpq5 \
    git \
    ssh \
    openjdk-11-jre-headless \
    && rm -rf /var/lib/apt/lists/*

# Copy installed Python packages and Spark from builder
COPY --from=builder /root/.local /root/.local
COPY --from=builder /opt/spark /opt/spark

# Create directories
RUN mkdir -p ${AIRFLOW_HOME}/dags \
    && mkdir -p ${AIRFLOW_HOME}/logs \
    && mkdir -p ${AIRFLOW_HOME}/plugins \
    && mkdir -p /opt/spark/work-dir

# Copy project files
WORKDIR ${AIRFLOW_HOME}
COPY data_pipeline/orchestration/dags/ ${AIRFLOW_HOME}/dags/
COPY data_pipeline/ ${AIRFLOW_HOME}/data_pipeline/
COPY monitoring/ ${AIRFLOW_HOME}/monitoring/

# Initialize Airflow
RUN airflow db init \
    && airflow users create \
    --username admin \
    --password admin \
    --firstname Admin \
    --lastname User \
    --role Admin \
    --email admin@william.com

# Expose ports
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Entrypoint
ENTRYPOINT ["airflow"]
CMD ["webserver"]