import logging
import re

import bleach

import config

logger = logging.getLogger(__name__)



# Padrões de Prompt Injection ─────────────────────────────────────────────────

_INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?(previous|prior)\s+instructions?",
    r"forget\s+(everything|all)",
    r"you\s+are\s+now\s+(a|an)",
    r"new\s+instructions?\s*:",
    r"system\s+prompt\s*:",
    r"jailbreak",
    r"do\s+anything\s+now",
]

_INJECTION_RE = re.compile("|".join(_INJECTION_PATTERNS), re.IGNORECASE)


# Tentativas de acessar informações sensíveis via ferramentas
_SENSITIVE_PATTERNS = [
    r"os\.environ",
    r"process\.env",
    r"\.env\b",
    r"api[_\s]?key",
    r"secret[_\s]?key",
    r"password",
    r"token",
    r"subprocess",
    r"__import__",
    r"exec\s*\(",
    r"eval\s*\(",
]

_SENSITIVE_RE = re.compile("|".join(_SENSITIVE_PATTERNS), re.IGNORECASE)


def validate_task(task: str) -> str:
  
    if not isinstance(task, str):
        raise TypeError("A tarefa deve ser uma string.")

    # Remove HTML
    clean = bleach.clean(task, tags=[], strip=True)
    clean = re.sub(r"\s+", " ", clean).strip()

    if not clean:
        raise ValueError("A tarefa não pode estar vazia.")

    if len(clean) > config.MAX_TASK_LENGTH:
        raise ValueError(
            f"Tarefa muito longa ({len(clean)} chars). "
            f"Máximo: {config.MAX_TASK_LENGTH}."
        )

    # Detecção de prompt injection
    if _INJECTION_RE.search(clean):
        logger.warning("Tentativa de prompt injection detectada: %r", clean[:50])
        raise ValueError("Tarefa contém conteúdo inválido.")

    # Detecção de tentativa de acessar dados sensíveis
    if _SENSITIVE_RE.search(clean):
        logger.warning("Tentativa de acessar dados sensíveis: %r", clean[:50])
        raise ValueError(
            "A tarefa contém termos não permitidos. "
            "Reformule sem referências a variáveis de sistema ou credenciais."
        )

    return clean


def validate_url(url: str) -> bool:
   
    url_lower = url.lower().strip()

    # Apenas HTTP e HTTPS
    if not url_lower.startswith(("http://", "https://")):
        raise ValueError(f"Protocolo não permitido: {url[:50]}")

    # Bloqueia acesso a recursos locais (SSRF)
    blocked_hosts = [
        "localhost", "127.0.0.1", "0.0.0.0",
        "169.254.",   # AWS metadata
        "192.168.",   # rede local
        "10.0.",      # rede privada
        "::1",        # IPv6 loopback
    ]
    for blocked in blocked_hosts:
        if blocked in url_lower:
            raise ValueError(f"URL não permitida: acesso a recurso local bloqueado.")

    return True


def validate_code_output(code: str) -> str:
    
    dangerous_patterns = [
        r"os\.system\s*\(",
        r"subprocess\.",
        r"shutil\.rmtree",
        r"rm\s+-rf",
        r"format\s+c:",
        r"__import__\s*\(\s*['\"]os['\"]",
    ]

    for pattern in dangerous_patterns:
        if re.search(pattern, code, re.IGNORECASE):
            logger.warning("Código potencialmente perigoso detectado.")
            return (
                "# AVISO: O agente gerou código que foi bloqueado por segurança.\n"
                "# Por favor, reformule a tarefa."
            )

    return code