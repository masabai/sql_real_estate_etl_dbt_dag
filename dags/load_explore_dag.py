from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.providers.slack.operators.slack_webhook import SlackWebhookOperator
from datetime import datetime
from etl.load_real_estate import etl_pipeline

# Default arguments for DAG tasks
default_args = {
    'owner': 'airflow',  # task owner
    'retries': 1,        # number of retries if task fails
}

# Define the DAG
with DAG(
    dag_id="load_explore_dag",
    default_args=default_args,
    start_date=datetime(2025, 12, 20),
    schedule_interval=None,  # manual trigger only
) as dag:

    # Task: Load CSV data into Postgres
    # Uses PythonOperator to run ETL pipeline
    load_task = PythonOperator(
        task_id="load_real_estate", #RealEstate/plugins/etl/load_explore_dag.py
        python_callable=etl_pipeline,
    )

    # SQL scripts to process data sequentially
    # Each script is run via BashOperator and psql
    sql_scripts = [
        "01_explore_raw_data.sql",
        "02_rename_columns.sql",
        "03_create_staging_view.sql",
        "04_profile_data_completeness.sql",
        "05_data_cleaning.sql",
        "06_eda.sql",
    ]

    previous_task = load_task

    for script in sql_scripts:
        # Generate unique task_id from the script filename prefix (e.g., "01", "02", "03")
        task_id = f"run_{script.split('_')[0]}"

        # Run SQL script using BashOperator
        sql_task = BashOperator(
            task_id=task_id,
            bash_command=(
                f"PGPASSWORD=airflow psql -h airflow_postgres -U airflow -d airflow "
                f"-f /opt/airflow/projects/sql_project/{script}"
            ),
        )
        # Set task dependency
        previous_task >> sql_task
        previous_task = sql_task

    # Task: Slack notification on success
    # Sends message if DAG completes successfully
    notify_slack_success = SlackWebhookOperator(
        task_id="notify_slack_success",
        http_conn_id="real_estate_slack",
        message="DAG load_explore_dag completed successfully!",
        trigger_rule="all_success",
    )

    # Task: Slack notification on failure
    # Sends message if any upstream task fails
    notify_slack_fail = SlackWebhookOperator(
        task_id="notify_slack_fail",
        http_conn_id="real_estate_slack",
        message="DAG load_explore_dag failed!",
        trigger_rule="one_failed",
    )

    # Chain last SQL task to Slack notifications
    previous_task >> [notify_slack_success, notify_slack_fail]
