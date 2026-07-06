FROM apache/airflow:2.8.1-python3.10

USER root

# Install system dependencies if required by any python packages (e.g., build-essential for psycopg2)
RUN apt-get update \
  && apt-get install -y --no-install-recommends \
         build-essential \
         libpq-dev \
  && apt-get autoremove -yqq --purge \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

USER airflow

# Copy requirements file (if it doesn't exist, we fallback to a manual pip install of known dependencies)
COPY --chown=airflow:root requirements.txt /requirements.txt

# Install python dependencies required by the pipeline
# We upgrade pip and install constraints matching the Airflow version to prevent dependency hell
RUN pip install --no-cache-dir "apache-airflow==${AIRFLOW_VERSION}" -r /requirements.txt
