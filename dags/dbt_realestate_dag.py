from airflow import DAG
from airflow.operators.bash import BashOperator
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

# passed - bash_command="cd /opt/airflow/projects/real_estate_dbt && dbt seed --target dev_airflow || true",
# passed- bash_command="cd /opt/airflow/projects/real_estate_dbt && dbt run --target dev_airflow || true",
# passed - bash_command="cd /opt/airflow/projects/real_estate_dbt && dbt test --target dev_airflow || true",