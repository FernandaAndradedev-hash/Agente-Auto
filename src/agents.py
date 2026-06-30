"""
Define os agentes da crew TaskMind.

"""
from crewai import Agent
from langchain_anthropic import ChatAnthropic

import config
from tools import CalculatorTool, CodeGeneratorTool, URLReaderTool, WebSearchTool

# LLM compartilhado entre os agentes
_llm = ChatAnthropic(
    model=config.LLM_MODEL,
    anthropic_api_key=config.ANTHROPIC_API_KEY,
    max_tokens=1024,
)


def create_researcher() -> Agent:
    """
    Agente especializado em pesquisa e coleta de informações.
    Usa busca web e leitura de URLs.
    """
    return Agent(
        role="Pesquisador Especialista",
        goal=(
            "Coletar informações precisas e atualizadas da internet "
            "para responder qualquer pergunta ou suportar qualquer tarefa."
        ),
        backstory=(
            "Você é um pesquisador meticuloso com anos de experiência em "
            "encontrar informações confiáveis na internet. Você sempre verifica "
            "múltiplas fontes, prioriza fontes oficiais e acadêmicas, e resume "
            "as informações de forma clara e objetiva. Você nunca inventa dados."
        ),
        tools=[WebSearchTool(), URLReaderTool()],
        llm=_llm,
        verbose=True,
        max_iter=config.MAX_ITERATIONS,
        allow_delegation=False,
    )


def create_executor() -> Agent:
    """
    Agente especializado em processar dados e gerar outputs.
    Usa calculadora e gerador de código.
    """
    return Agent(
        role="Executor e Analista",
        goal=(
            "Processar informações coletadas, realizar cálculos necessários "
            "e gerar código Python quando solicitado."
        ),
        backstory=(
            "Você é um analista técnico experiente que transforma dados brutos "
            "em respostas claras e acionáveis. Quando precisa de cálculos, "
            "você usa a calculadora para garantir precisão. Quando precisa gerar "
            "código, você escreve Python limpo, bem comentado e funcional. "
            "Você sempre apresenta resultados de forma organizada."
        ),
        tools=[CalculatorTool(), CodeGeneratorTool()],
        llm=_llm,
        verbose=True,
        max_iter=config.MAX_ITERATIONS,
        allow_delegation=False,
    )