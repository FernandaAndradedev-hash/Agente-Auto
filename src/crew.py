import logging

from crewai import Crew, Process

from agents import create_executor, create_researcher
from tasks import create_execution_task, create_research_task
from validators import validate_task

logger = logging.getLogger(__name__)


def run_task(user_input: str) -> str:
    """
    Executa uma tarefa com a crew TaskMind.

    Args:
        user_input: Tarefa do usuário em linguagem natural.

    Returns:
        Resultado final gerado pela crew.
    """
    # Sanitiza a entrada
    clean_task = validate_task(user_input)

    # Cria os agentes
    researcher = create_researcher()
    executor = create_executor()

    # Cria as tarefas
    research_task = create_research_task(clean_task, researcher)
    execution_task = create_execution_task(clean_task, executor, [research_task])

    # Monta e executa a crew
    crew = Crew(
        agents=[researcher, executor],
        tasks=[research_task, execution_task],
        process=Process.sequential,  # research → execution
        verbose=True,
    )

    logger.info("Iniciando crew para tarefa: '%s...'", clean_task[:50])
    result = crew.kickoff()

    return str(result)