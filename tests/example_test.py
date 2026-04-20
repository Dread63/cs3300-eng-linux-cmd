# test_command_assistant.py
import pytest
from unittest.mock import Mock, patch, MagicMock
from explainer import CommandExplainer, ExplanationResult
from ollama_client import ollama_client, TranslationResult, _parse_response
from security import validate_command, run_command

# === 1. Unit Tests ===

def test_validate_command_blocks_dangerous():
    """TC-10 to TC-16: Security validation"""
    assert validate_command("rm -rf /") == False
    assert validate_command("rm -rf *") == False
    assert validate_command("rm file.txt") == True
    assert validate_command("sudo apt update") == True

def test_parse_response_perfect_format():
    """TC-21: Perfect LLM response"""
    raw = "COMMAND: ls -la\nCONFIDENCE: high\nWARNING: none"
    result = _parse_response(raw)
    assert result.success == True
    assert result.command == "ls -la"
    assert result.confidence == "high"

def test_parse_response_missing_sections():
    """TC-24: Missing confidence/warning"""
    raw = "COMMAND: pwd"
    result = _parse_response(raw)
    assert result.success == True
    assert result.command == "pwd"
    assert result.confidence == "medium"  # Default

def test_explainer_parse_structured_response():
    """TC-17 to TC-20: Explanation parsing"""
    explainer = CommandExplainer(Mock())
    raw = """SUMMARY: Lists all files in long format
BREAKDOWN:
- -l: Shows detailed info
- -a: Shows hidden files
WARNING: none"""
    
    result = explainer._parse_response(raw)
    assert result.success == True
    assert "lists all files" in result.summary.lower()
    assert len(result.breakdown) == 2
    assert result.warning == ""

# === 2. Integration Tests (with mocked LLM) ===

@pytest.fixture
def mock_llm():
    mock = Mock()
    mock.create_chat_completion.return_value = {
        "choices": [{"message": {"content": "COMMAND: ls\nCONFIDENCE: high\nWARNING: none"}}]
    }
    return mock

def test_ollama_client_integration(mock_llm, tmp_path):
    """Test full translation flow with mocked LLM"""
    with patch('ollama_client.llm', mock_llm):
        with patch('ollama_client.ChatSession') as MockSession:
            MockSession.return_value.chat_history_file = tmp_path / "history.json"
            result = ollama_client("list files")
            assert result.success == True
            assert result.command == "ls"

def test_cli_loop_explain_mode():
    """Test explanation flag triggers explainer"""
    # This would need mocking of input() and display functions
    pass

# === 3. End-to-End Tests ===

def test_end_to_end_safe_command():
    """Full workflow: request → generate → validate → execute"""
    # Use subprocess to run your actual CLI
    import subprocess
    result = subprocess.run(
        ['python', 'main.py'],
        input='list files\nexit\n',
        capture_output=True,
        text=True
    )
    assert "Suggested Command:" in result.stdout

# === 4. Property-Based Tests (using Hypothesis) ===

from hypothesis import given, strategies as st

@given(st.text(min_size=1, max_size=100))
def test_parse_response_never_crashes(raw_response):
    """Any text input to _parse_response should not crash"""
    result = _parse_response(raw_response)
    assert isinstance(result, TranslationResult)

# === 5. Snapshot Tests ===

def test_explainer_output_structure_snapshot():
    """Ensure explanation format doesn't regress"""
    explainer = CommandExplainer(Mock())
    # Mock LLM to return known response
    # Compare against stored snapshot file
    pass