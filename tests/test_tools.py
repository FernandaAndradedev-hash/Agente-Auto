import os
os.environ.setdefault("ANTHROPIC_API_KEY", "sk-ant-test-fake")
os.environ.setdefault("SERPER_API_KEY", "test-serper-key")

from unittest.mock import MagicMock, patch
import pytest
from tools import CalculatorTool, URLReaderTool


class TestCalculatorTool:

    def setup_method(self):
        self.calc = CalculatorTool()

    def test_soma_simples(self):
        result = self.calc._run("2 + 2")
        assert "4" in result

    def test_multiplicacao(self):
        result = self.calc._run("10 * 5")
        assert "50" in result

    def test_divisao(self):
        result = self.calc._run("100 / 4")
        assert "25" in result

    def test_potenciacao(self):
        result = self.calc._run("2 ** 10")
        assert "1024" in result

    def test_sqrt(self):
        result = self.calc._run("sqrt(144)")
        assert "12" in result

    def test_expressao_complexa(self):
        result = self.calc._run("(1500 * 0.15) + 200")
        assert "425" in result

    def test_divisao_por_zero(self):
        result = self.calc._run("10 / 0")
        assert "zero" in result.lower()

    def test_expressao_invalida(self):
        result = self.calc._run("print('hack')")
        assert "inválida" in result.lower() or "não permitida" in result.lower()

    def test_import_bloqueado(self):
        result = self.calc._run("__import__('os')")
        assert "inválida" in result.lower() or "não permitida" in result.lower()


class TestURLReaderTool:

    def setup_method(self):
        self.reader = URLReaderTool()

    @patch("tools.httpx.Client")
    def test_leitura_url_valida(self, mock_client_class):
        mock_response = MagicMock()
        mock_response.text = "<html><body><p>Conteúdo de teste</p></body></html>"
        mock_response.raise_for_status = MagicMock()
        mock_client_class.return_value.__enter__.return_value.get.return_value = mock_response

        result = self.reader._run("https://example.com")
        assert "Conteúdo de teste" in result

    def test_localhost_bloqueado(self):
        result = self.reader._run("http://localhost:8000")
        assert "bloqueada" in result.lower()

    def test_url_sem_https_bloqueada(self):
        result = self.reader._run("ftp://example.com")
        assert "bloqueada" in result.lower() or "Protocolo" in result