from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.providers.slack.operators.slack_webhook import SlackWebhookOperator
from datetime import datetime
from etl.load_real_estate import etl_pipeline

default_args = {
    'owner': 'airflow',
    'retries': 1,
}

with DAG(
    dag_id="load_explore_dag",
    default_args=default_args,
    start_date=datetime(2025, 8, 1),
    schedule_interval=None,
    catchup=False,
) as dag:

    # Load CSV into Postgres
    load_task = PythonOperator(
        task_id="load_real_estate",
        python_callable=etl_pipeline,
    )

    # SQL scripts tasks
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
        task_id = f"run_{script.split('_')[0]}"  # create task_id from filename prefix
        sql_task = BashOperator(
            task_id=task_id,
            bash_command=(
                f"PGPASSWORD=airflow psql -h airflow_postgres -U airflow -d airflow "
                f"-f /opt/airflow/projects/sql_project/{script}"
            ),
        )
        previous_task >> sql_task
        previous_task = sql_task

    # Slack success notification
    notify_slack_success = SlackWebhookOperator(
        task_id="notify_slack_success",
        http_conn_id="slack916",
        message=":rocket: DAG load_explore_dag completed successfully!",
        trigger_rule="all_success",
    )

    # Slack failure notification
    notify_slack_fail = SlackWebhookOperator(
        task_id="notify_slack_fail",
        http_conn_id="slack916",
        message=":x: DAG load_explore_dag failed!",
        trigger_rule="one_failed",
    )

    # Chain last SQL task to Slack notifications
    previous_task >> [notify_slack_success, notify_slack_fail]
