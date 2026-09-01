import os
import sys
import subprocess
import pytest

def run_ai_validation_suite():
    """
    Main orchestrator to execute the entire AI QA Testing Framework.
    Configures environment paths and runs all 3 security, repair, 
    and workflow integration test suites with verbose reporting.
    """
    print("=" * 80)
    print("🚀 INITIALIZING TREND AI TEST ENGINEER II VALIDATION FRAMEWORK")
    print("=" * 80)

    # 1. Define the specific target test files in order of execution
    test_files = [
        "tests/test_ai_security.py",   # Layer 1: Input Guardrails & Injection Security
        "tests/test_ai_repair.py",     # Layer 2: LLM Auto-Repair Fallback Logic
        "tests/test_ai_pipeline_workflow.py" # Layer 3: End-to-End Agent Integration
    ]

    # 2. Build pytest arguments (-v for line-by-line, -W ignore to hide Airflow warnings)
    pytest_args = [
        "-v",
        "-W", "ignore",
        "--tb=short" # Keeps tracebacks clean and scannable
    ] + test_files

    # 3. Execute the suite via pytest engine
    print(f"📸 Scanning framework directories... Found {len(test_files)} core validation modules.")
    print("🏃 Executing programmatic test loops inside container space...\n")
    
    exit_code = pytest.main(pytest_args)

    # 4. Process framework completion status
    print("\n" + "=" * 80)
    if exit_code == pytest.ExitCode.OK:
        print("🎯 FRAMEWORK STATUS: SUCCESS (All automated AI safety grids passed!)")
    else:
        print("🚨 FRAMEWORK STATUS: FAILED (Anomalies or guardrail breaches detected)")
    print("=" * 80)

    sys.exit(exit_code)

if __name__ == "__main__":
    run_ai_validation_suite()
