import logging
import sys

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

from crew import run_task
from validators import validate_task

logging.basicConfig(level=logging.WARNING)
console = Console()


def print_banner():
    console.print(Panel.fit(
        "[bold cyan]TaskMind Agent[/bold cyan]\n"
        "[dim]Agente autônomo com CrewAI — busca, cálculo e código[/dim]",
        border_style="cyan",
    ))


def main():
    print_banner()
    console.print("\n[dim]Digite sua tarefa ou 'sair' para encerrar.[/dim]\n")

    while True:
        try:
            user_input = Prompt.ask("[cyan]Tarefa[/cyan]")

            if user_input.lower().strip() in {"sair", "exit", "quit"}:
                console.print("[dim]Encerrando TaskMind. Até logo![/dim]")
                break

            # Valida antes de processar
            try:
                validate_task(user_input)
            except ValueError as exc:
                console.print(f"[red]Entrada inválida:[/red] {exc}")
                continue

            console.print("\n[dim]Processando...[/dim]\n")

            result = run_task(user_input)

            console.print(Panel(
                result,
                title="[bold green]Resultado[/bold green]",
                border_style="green",
            ))
            console.print()

        except KeyboardInterrupt:
            console.print("\n[dim]Interrompido pelo usuário.[/dim]")
            break
        except Exception as exc:
            console.print(f"[red]Erro:[/red] {exc}")


if __name__ == "__main__":
    main()