import os
os.environ.setdefault("ANTHROPIC_API_KEY", "sk-ant-test-fake")
os.environ.setdefault("SERPER_API_KEY", "test-key")

from unittest.mock import patch, MagicMock
import pytest


class TestCrew:

    @patch("crew.Crew")
    @patch("crew.create_execution_task")
    @patch("crew.create_research_task")
    @patch("crew.create_researcher")
    @patch("crew.create_executor")
    def test_run_task_valida(self, mock_executor, mock_researcher, mock_research_task, mock_execution_task, mock_crew_class):
        mock_crew = MagicMock()
        mock_crew.kickoff.return_value = "Resultado da tarefa"
        mock_crew_class.return_value = mock_crew
        mock_researcher.return_value = MagicMock()
        mock_executor.return_value = MagicMock()
        mock_research_task.return_value = MagicMock()
        mock_execution_task.return_value = MagicMock()

        from crew import run_task
        result = run_task("Qual é a capital do Brasil?")
        assert isinstance(result, str)