# Agente-Autônomo
 
> Agente autônomo com CrewAI que executa tarefas em linguagem natural usando busca web, cálculo matemático e geração de código Python.
---
 
## Funcionalidades
 
- Busca informações atuais na web via Serper API
- Realiza cálculos matemáticos com precisão
- Gera scripts Python funcionais e comentados
- Lê conteúdo de páginas web
- Proteção contra prompt injection e SSRF
- Testes unitários com cobertura de segurança
 
---
 
## Stack
 
| Camada | Tecnologia |
|--------|-----------|
| Framework de agentes | CrewAI |
| LLM | Anthropic Claude Haiku |
| Busca web | Serper API |
| Interface | Rich (CLI) |
 
---
 
## Como rodar
 
```bash
git clone https://github.com/FernandaAndradedev-hash/Agente-Auto.git
cd Agente-Auto
py -3.11 -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
# Preencha ANTHROPIC_API_KEY e SERPER_API_KEY no .env
 
python src/cli.py
```
 
## Exemplos de tarefas
 
````
Qual é o PIB do Brasil em 2024?
Calcule quanto é 15% de R$ 3.750,00
Gere um script Python para ler um CSV e calcular a média de uma coluna
Quanto custa 1 dólar hoje em reais?
````
 
---
 
## Testes
 
```bash
pytest tests/ -v
```
 
---
 
## Estrutura
 
````
Agente-Auto/
├── src/
│   ├── config.py      # Configurações
│   ├── validators.py  # Segurança
│   ├── tools.py       # Ferramentas do agente
│   ├── agents.py      # Definição dos agentes
│   ├── tasks.py       # Definição das tarefas
│   ├── crew.py        # Orquestrador
│   └── cli.py         # Interface CLI
├── tests/
````
 
---
## Licença
 Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.
 
 ---