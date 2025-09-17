from airflow.models import DAG
from airflow.operators.bash import BashOperator
from airflow.providers.slack.operators.slack_webhook import SlackWebhookOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'airflow',
    'retries': 1,
}

with DAG(
    dag_id="dbt_realestate_dag",
    default_args=default_args,
    start_date=datetime(2025, 8, 25),
    schedule_interval=None,
    catchup=False,
) as dag:

    # Run dbt build
    run_dbt = BashOperator(
        task_id="run_dbt",
        bash_command=(
            "cd /opt/airflow/projects/real_estate_dbt && "
            "dbt build --target dev_airflow || true"
        ),
        do_xcom_push=False,
        retries=0
    )

    # Slack success notification
    notify_slack_success = SlackWebhookOperator(
        task_id="notify_slack_success",
        http_conn_id="slack915",  # make sure Webhook Token = full URL in Airflow UI
        message=":rocket: DAG dbt_realestate_dag completed successfully!",
        trigger_rule="all_success",  # only runs if all upstream tasks succeed
    )

    # Slack failure notification
    notify_slack_fail = SlackWebhookOperator(
        task_id="notify_slack_fail",
        http_conn_id="slack915",
        message=":x: DAG dbt_realestate_dag failed!",
        trigger_rule="one_failed",  # runs if any upstream task fails
    )

    # Chain tasks
    run_dbt >> [notify_slack_success, notify_slack_fail]
