import pytest
from unittest.mock import MagicMock, patch

MOCK_SCHEMA = "fact_sales (town TEXT, sale_amount FLOAT, date_recorded DATE)"

@pytest.fixture
def mock_pipeline_lifecycle():
    """Chains side-effects to simulate generate_sql failing and repair_sql succeeding."""
    with patch("rag.config.client.chat.completions.create") as mock_create:
        # First call output: Malformed generation statement containing a misplaced semicolon
        mock_gen_response = MagicMock()
        mock_gen_response.choices = [
            MagicMock(message=MagicMock(content="```sql\nSELECT town, SUM(sale_amount); FROM fact_sales\n```"))
        ]
        
        # Second call output: Clean, recovered star-schema query format
        mock_repair_response = MagicMock()
        mock_repair_response.choices = [
            MagicMock(message=MagicMock(content="```sql\nSELECT fs.town, ROUND((SUM(fs.sale_amount))::numeric, 2) FROM fact_sales fs GROUP BY fs.town\n```"))
        ]
        
        mock_create.side_effect = [mock_gen_response, mock_repair_response]
        yield mock_create

# --- AUTOMATED TEST SCENARIOS ---

def test_end_to_end_ai_agent_healing_workflow(mock_pipeline_lifecycle):
    """Simulate end-to-end multi-step orchestration from translation failure to repair recovery."""
    from rag.config import generate_sql, repair_sql
    
    user_question = "What is the total sales amount for each town?"
    
    # 1. Trigger initial translation agent step
    initial_generated_sql = generate_sql(user_question, MOCK_SCHEMA)
    
    # 2. Programmatic validation interceptor checks for syntax anomalies
    is_valid_syntax = ";" not in initial_generated_sql.replace(initial_generated_sql[-1], "") 
    
    # 3. Route to repair workflow fallback logic if an anomaly is flagged
    if not is_valid_syntax:
        simulated_db_error = "Syntax error near FROM"
        final_executable_sql = repair_sql(
            question=user_question,
            bad_sql=initial_generated_sql,
            error=simulated_db_error,
            schema_context=MOCK_SCHEMA
        )
    else:
        final_executable_sql = initial_generated_sql

    # 4. Final verification checks against required business metrics
    assert "fs" in final_executable_sql, "Rule Violation: Explicit table aliases are missing."
    assert "ROUND" in final_executable_sql, "Rule Violation: Output missed strict currency rounding rules."
    assert "GROUP BY" in final_executable_sql, "Rule Violation: Aggregated data structure missing structural grouping statements."
