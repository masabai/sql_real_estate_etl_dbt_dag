from airflow.models import DAG
from airflow.operators.bash import BashOperator
from airflow.providers.slack.operators.slack_webhook import SlackWebhookOperator
from datetime import datetime, timedelta

# Default arguments applied to all tasks in the DAG
default_args = {
    'owner': 'airflow',  # task owner
    'retries': 1,        # number of retries if task fails
}

# Define the DAG
with DAG(
    dag_id="dbt_realestate_dag",
    default_args=default_args,
    start_date=datetime(2025, 12, 20),
    schedule_interval=None,  # manual trigger only
) as dag:

    # Task: Run dbt build
    # Executes dbt build command in the project folder
    run_dbt = BashOperator(
        task_id="run_dbt",
        bash_command=(
            "cd /opt/airflow/projects/real_estate_dbt && "
            "dbt build --target dev_airflow || true"
        ),
        do_xcom_push=False,  # do not push stdout to Airflow Admin/XCom
        retries=0
    )

    # Task: Slack notification on success
    # Sends message if dbt build succeeds
    notify_slack_success = SlackWebhookOperator(
        task_id="notify_slack_success",
        http_conn_id="real_estate_slack",  # Webhook token configured in Airflow UI, Conn Id
        message="DAG dbt_realestate_dag completed successfully!",
        trigger_rule="all_success",
    )

    # Task: Slack notification on failure
    # Sends message if any upstream task fails
    notify_slack_fail = SlackWebhookOperator(
        task_id="notify_slack_fail",
        http_conn_id="real_estate_slack",
        message="DAG dbt_realestate_dag failed!",
        trigger_rule="one_failed",
    )

    # Define task order / dependencies
    run_dbt >> [notify_slack_success, notify_slack_fail]
