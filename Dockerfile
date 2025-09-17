# Use the official Airflow 2.7.0 image
FROM apache/airflow:2.7.0

# Switch to root to install packages
USER airflow 

# Install dbt and Postgres adapter
RUN pip install --no-cache-dir dbt-core dbt-postgres

# Switch back to airflow user
USER airflow
