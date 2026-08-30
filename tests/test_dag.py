import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
pytest.importorskip("airflow", reason="airflow not installed — skipping DAG tests")

from airflow.models import DagBag

# Define the explicit map of DAGs and their expected tasks
DAG_TEST_MATRIX = [
    {
        "file": "/opt/airflow/dags/dbt_realestate_dag.py",
        "dag_id": "dbt_realestate_dag",
        "tasks": {"run_dbt", "notify_slack_success", "notify_slack_fail"}
    },
    {
        "file": "/opt/airflow/dags/load_explore_dag.py",
        "dag_id": "load_explore_dag",
        "tasks": {"load_real_estate","notify_slack_success", "notify_slack_fail"} # 👈 Add your exact task names for this DAG here
    }
]

@pytest.fixture(scope="function")
def targeted_dagbag(request):
    """Dynamically load ONLY the specific DAG file being tested right now."""
    dag_meta = request.param
    bag = DagBag(dag_folder=dag_meta["file"], include_examples=False)
    return {
        "bag": bag,
        "dag_id": dag_meta["dag_id"],
        "expected_tasks": dag_meta["tasks"],
        "file_path": dag_meta["file"]
    }

# This decorator forces pytest to run every test below TWICE (once for each DAG metadata dict)
@pytest.mark.parametrize("targeted_dagbag", DAG_TEST_MATRIX, indirect=True, ids=["dbt_dag", "load_dag"])
class TestAirflowDags:

    def test_dag_loads_no_errors(self, targeted_dagbag):
        """Confirm the specific DAG file has zero syntax or import issues."""
        bag = targeted_dagbag["bag"]
        file_path = targeted_dagbag["file_path"]
        
        # Isolate import errors strictly to the current file under test
        file_errors = {k: v for k, v in bag.import_errors.items() if file_path in k}
        assert file_errors == {}, f"DAG import errors found: {file_errors}"

    def test_dag_exists(self, targeted_dagbag):
        """Verify the expected DAG ID was found inside its respective file."""
        bag = targeted_dagbag["bag"]
        target_id = targeted_dagbag["dag_id"]
        assert target_id in bag.dags, f"DAG ID '{target_id}' was not found in the file structure."

    def test_dag_has_expected_tasks(self, targeted_dagbag):
        """Check that the correct target tasks exist within the active DAG structure."""
        bag = targeted_dagbag["bag"]
        target_id = targeted_dagbag["dag_id"]
        expected = targeted_dagbag["expected_tasks"]
        
        dag = bag.dags[target_id]
        actual_tasks = {t.task_id for t in dag.tasks}
        
        # Uses sub-set matching so the test doesn't break if you add more tasks later
        assert expected.issubset(actual_tasks), f"Missing required tasks in {target_id}. Found: {actual_tasks}"

    def test_dag_task_order(self, targeted_dagbag):
        """Verify that the common Slack alert steps depend directly on upstream tasks."""
        bag = targeted_dagbag["bag"]
        target_id = targeted_dagbag["dag_id"]
        dag = bag.dags[target_id]
        
        # Both DAGs use these notification modules
        success_upstream = dag.get_task("notify_slack_success").upstream_task_ids
        fail_upstream = dag.get_task("notify_slack_fail").upstream_task_ids
        
        assert len(success_upstream) > 0, f"notify_slack_success has no upstream targets in {target_id}"
        assert len(fail_upstream) > 0, f"notify_slack_fail has no upstream targets in {target_id}"
