import pytest
from unittest.mock import MagicMock, patch

@pytest.fixture
def mock_groq_client():
    """Mocks the Groq completion response to avoid burning API tokens during tests."""
    with patch("rag.config.client.chat.completions.create") as mock_create:
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(message=MagicMock(content="```sql\nSELECT fs.town, ROUND((SUM(fs.sale_amount))::numeric, 2) FROM fact_sales fs GROUP BY fs.town\n```"))
        ]
        mock_create.return_value = mock_response
        yield mock_create

# --- AUTOMATED TEST SCENARIOS ---

def test_repair_sql_removes_markdown_and_semicolons(mock_groq_client):
    """Verify that string hygiene guardrails strip out raw LLM markdown blocks and trailing symbols."""
    from rag.config import repair_sql
    
    sample_schema = "fact_sales (town TEXT, sale_amount FLOAT)"
    
    repaired_sql = repair_sql(
        question="Show total sales by town",
        bad_sql="SELECT town, SUM(sale_amount); FROM fact_sales",
        error="Syntax error at or near ';'",
        schema_context=sample_schema
    )
    
    assert "```sql" not in repaired_sql, "Sanitation Failure: Markdown wrappers leaked to compiler!"
    assert "```" not in repaired_sql, "Sanitation Failure: Code blocks characters left behind!"
    assert not repaired_sql.endswith(";"), "Sanitation Failure: Trailing semicolon was not removed!"
    assert repaired_sql.startswith("SELECT"), "Structure Failure: Response did not resolve to clean query code."
