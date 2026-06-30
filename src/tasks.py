from crewai import Task

from agents import create_executor, create_researcher


def create_research_task(user_task: str, researcher) -> Task:
    """Tarefa de pesquisa — executada pelo Researcher."""
    return Task(
        description=(
            f"Pesquise na internet as informações necessárias para completar "
            f"a seguinte tarefa: {user_task}\n\n"
            f"Se a tarefa não requerer pesquisa (ex: cálculo puro ou geração "
            f"de código simples), informe isso claramente e passe para o próximo agente."
        ),
        expected_output=(
            "Informações relevantes encontradas na web, com fontes citadas. "
            "Se não foi necessário pesquisar, explique por quê."
        ),
        agent=researcher,
    )


def create_execution_task(user_task: str, executor, context_tasks: list) -> Task:
    """Tarefa de execução — usa o contexto da pesquisa."""
    return Task(
        description=(
            f"Com base nas informações pesquisadas, complete a tarefa: {user_task}\n\n"
            f"Se a tarefa envolver cálculos, use a Calculadora. "
            f"Se pedir código Python, use o Gerador de Código. "
            f"Apresente o resultado final de forma clara e completa."
        ),
        expected_output=(
            "Resultado completo e bem formatado da tarefa. "
            "Se incluir cálculos, mostre os valores. "
            "Se incluir código, apresente o código completo."
        ),
        agent=executor,
        context=context_tasks,
    )