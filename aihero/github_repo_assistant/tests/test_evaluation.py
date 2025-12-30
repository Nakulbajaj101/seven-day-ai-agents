import os
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pandas as pd
import pytest

from evaluation import (
    EVALUATION_SYSTEM_PROMPT,
    EvaluationCheck,
    EvaluationChecklist,
    build_evaluations_df,
    get_eval_data,
    load_log_data,
    simplify_log_messages,
)

# Test Data
SAMPLE_MESSAGES = [
    {
        "kind": "request",
        "parts": [{"part_kind": "user-prompt", "content": "Hello", "timestamp": 123}]
    },
    {
        "kind": "response",
        "parts": [{"part_kind": "text", "content": "Hi there", "id": "abc"}]
    }
]

def test_simplify_log_messages():
    simplified = simplify_log_messages(SAMPLE_MESSAGES)
    
    assert len(simplified) == 2
    # Check simplified user prompt
    assert simplified[0]['parts'][0]['content'] == "Hello"
    assert 'timestamp' not in simplified[0]['parts'][0]
    
    # Check simplified response
    assert simplified[1]['parts'][0]['content'] == "Hi there"
    assert 'id' not in simplified[1]['parts'][0]

def test_build_evaluations_df():
    # Mock data
    mock_record = {"log_file": "test_log.json", "source": "ai-generated", "model": "gpt-4"}
    
    mock_checks = [
        EvaluationCheck(check_name="test_pass", check_pass=True, justification="Good"),
        EvaluationCheck(check_name="test_fail", check_pass=False, justification="Bad")
    ]
    mock_result = EvaluationChecklist(checks=mock_checks, summary="Summary")
    
    eval_results = [(mock_result, mock_record)]
    
    df = build_evaluations_df(eval_results)
    
    assert len(df) == 1
    assert df.iloc[0]['log_file'] == "test_log.json"
    assert df.iloc[0]['test_pass'] == True
    assert df.iloc[0]['test_fail'] == False

# Integration-like tests with mocks
@pytest.mark.asyncio
async def test_evaluation_flow():
    # Mock Agent
    mock_agent = AsyncMock()
    mock_return = EvaluationChecklist(
        checks=[EvaluationCheck(check_name="relevant", check_pass=True, justification="Yes")],
        summary="Good job"
    )
    # Mock the return value of agent.run().output
    mock_run_result = MagicMock()
    mock_run_result.output = mock_return
    mock_agent.run.return_value = mock_run_result
    
    from evaluation import evaluate_log_record
    
    log_record = {
        "messages": SAMPLE_MESSAGES,
        "system_prompt": ["You are a bot"]
    }
    
    result = await evaluate_log_record(mock_agent, log_record)
    
    assert result.checks[0].check_name == "relevant"
    assert result.checks[0].check_pass == True

def test_data_loading_filtering(tmp_path):
    # Create dummy json files
    d = tmp_path / "logs"
    d.mkdir()
    
    # File 1: Valid AI generated
    p1 = d / "log1.json"
    p1.write_text('{"source": "ai-generated", "messages": []}')
    
    # File 2: User generated (should skip)
    p2 = d / "log2.json"
    p2.write_text('{"source": "user", "messages": []}')
    
    # File 3: Invalid JSON
    p3 = d / "log3.json"
    p3.write_text('{invalid}')
    
    eval_data = get_eval_data(d)
    
    assert len(eval_data) == 1
    assert eval_data[0]['log_file'] == "log1.json"
