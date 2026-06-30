import json
import logging
import math
import re

import httpx
from crewai.tools import BaseTool
from pydantic import Field

import config
from validators import validate_url

logger = logging.getLogger(__name__)


class WebSearchTool(BaseTool):
    """
    Ferramenta de busca na web via Serper API.

    """
    name: str = "Busca Web"
    description: str = (
        "Use esta ferramenta para buscar informações atuais na internet. "
        "Útil para: dados recentes, notícias, fatos, preços, estatísticas, "
        "informações sobre empresas, pessoas ou eventos. "
        "Input: uma query de busca em português ou inglês. "
        "Output: lista de resultados com título, snippet e URL."
    )

    def _run(self, query: str) -> str:
        """Executa busca via Serper API."""
        try:
            with httpx.Client(timeout=10.0) as client:
                response = client.post(
                    "https://google.serper.dev/search",
                    headers={
                        "X-API-KEY": config.SERPER_API_KEY,
                        "Content-Type": "application/json",
                    },
                    json={"q": query, "gl": "br", "hl": "pt", "num": 5},
                )
                response.raise_for_status()
                data = response.json()

            results = data.get("organic", [])
            if not results:
                return "Nenhum resultado encontrado para esta busca."

            formatted = []
            for i, r in enumerate(results[:5], 1):
                formatted.append(
                    f"{i}. {r.get('title', '')}\n"
                    f"   {r.get('snippet', '')}\n"
                    f"   URL: {r.get('link', '')}"
                )

            return "\n\n".join(formatted)

        except httpx.HTTPStatusError as exc:
            logger.error("Serper API erro: %s", exc)
            return f"Erro na busca: {exc.response.status_code}"
        except Exception as exc:
            logger.error("Erro inesperado na busca: %s", exc)
            return f"Erro ao buscar: {str(exc)}"


class CalculatorTool(BaseTool):
    """Ferramenta de cálculo matemático seguro."""

    name: str = "Calculadora"
    description: str = (
        "Use para realizar cálculos matemáticos. "
        "Suporta: operações básicas (+, -, *, /), potenciação (**), "
        "raiz quadrada (sqrt), logaritmo (log), seno/cosseno (sin, cos), "
        "porcentagem, e expressões complexas. "
        "Input: expressão matemática como string. "
        "Exemplo: '(1500 * 0.15) + 200' ou 'sqrt(144)'. "
        "NÃO use para texto — apenas expressões numéricas."
    )

    # Funções matemáticas permitidas
    _ALLOWED_NAMES = {
        "sqrt": math.sqrt,
        "log": math.log,
        "log10": math.log10,
        "sin": math.sin,
        "cos": math.cos,
        "tan": math.tan,
        "pi": math.pi,
        "e": math.e,
        "abs": abs,
        "round": round,
        "pow": pow,
    }

    def _run(self, expression: str) -> str:
        """
        Avalia expressão matemática de forma segura.

        """
        import ast

        # Remove espaços extras e normaliza
        expr = expression.strip()

        # Verifica se contém apenas caracteres permitidos
        if not re.match(r"^[\d\s\+\-\*\/\(\)\.\,\_a-zA-Z]+$", expr):
            return f"Expressão inválida: '{expr}'. Use apenas números e operadores matemáticos."

        try:
            # Parse a expressão como AST para validação
            tree = ast.parse(expr, mode="eval")

            # Verifica nós permitidos
            allowed_nodes = (
                ast.Expression, ast.BinOp, ast.UnaryOp, ast.Num,
                ast.Constant, ast.Call, ast.Name, ast.Load,
                ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Pow,
                ast.Mod, ast.USub, ast.UAdd,
            )

            for node in ast.walk(tree):
                if not isinstance(node, allowed_nodes):
                    return f"Operação não permitida na expressão."
                if isinstance(node, ast.Name) and node.id not in self._ALLOWED_NAMES:
                    return f"Função '{node.id}' não permitida."

            # Avalia de forma segura
            result = eval(
                compile(tree, "<string>", "eval"),
                {"__builtins__": {}},
                self._ALLOWED_NAMES,
            )

            return f"Resultado: {result}"

        except ZeroDivisionError:
            return "Erro: divisão por zero."
        except Exception as exc:
            return f"Erro ao calcular '{expr}': {str(exc)}"


class CodeGeneratorTool(BaseTool):
    """Ferramenta de geração de código Python."""

    name: str = "Gerador de Código Python"
    description: str = (
        "Use para gerar scripts Python que resolvam um problema específico. "
        "Útil quando o usuário precisa de código para automatizar algo, "
        "processar dados, criar scripts ou implementar algoritmos. "
        "Input: descrição do que o código deve fazer. "
        "Output: código Python funcional e comentado. "
        "IMPORTANTE: apenas gera o código, não executa."
    )

    def _run(self, description: str) -> str:
        """
        Gera código Python via Claude.

        """
        import anthropic
        from validators import validate_code_output

        client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)

        prompt = f"""Gere um script Python funcional para: {description}

Requisitos:
- Código limpo e bem comentado
- Inclua docstring na função principal
- Use boas práticas Python (PEP 8)
- Inclua exemplo de uso ao final
- NÃO inclua código que acesse variáveis de ambiente, credenciais ou execute comandos do sistema

Responda APENAS com o código Python, sem explicações adicionais."""

        response = client.messages.create(
            model=config.LLM_MODEL,
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}],
        )

        code = response.content[0].text

        # Remove backticks de markdown se presentes
        code = re.sub(r"```python\n?", "", code)
        code = re.sub(r"```\n?", "", code)
        code = code.strip()

        # Valida o código antes de retornar
        return validate_code_output(code)


class URLReaderTool(BaseTool):
    """Ferramenta para ler conteúdo de páginas web."""

    name: str = "Leitor de URL"
    description: str = (
        "Use para ler o conteúdo de uma página web específica quando você "
        "já tem a URL e precisa do conteúdo completo. "
        "Diferente da busca web, esta ferramenta acessa uma URL diretamente. "
        "Input: URL completa (deve começar com https://). "
        "Output: texto extraído da página."
    )

    def _run(self, url: str) -> str:
        """Lê e extrai texto de uma URL."""
        try:
            validate_url(url)

            with httpx.Client(
                timeout=10.0,
                follow_redirects=True,
                headers={"User-Agent": "TaskMind-Agent/1.0"},
            ) as client:
                response = client.get(url)
                response.raise_for_status()

            # Extração simples de texto — remove tags HTML
            text = re.sub(r"<[^>]+>", " ", response.text)
            text = re.sub(r"\s+", " ", text).strip()

            # Limita o tamanho do conteúdo retornado
            if len(text) > 3000:
                text = text[:3000] + "... [conteúdo truncado]"

            return text

        except ValueError as exc:
            return f"URL bloqueada: {exc}"
        except httpx.HTTPStatusError as exc:
            return f"Erro HTTP {exc.response.status_code} ao acessar {url}"
        except Exception as exc:
            return f"Erro ao ler URL: {str(exc)}"