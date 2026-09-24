"""Testes unitarios do conversor de moedas.

Como rodar (na pasta do projeto, ao lado do conversor.py):
    python -m unittest -v
"""

import io
import os
import unittest
from contextlib import redirect_stdout
from unittest.mock import Mock, patch
import requests
import conversor

def resposta_falsa(dados):
    # Cria uma resposta de API falsa cujo .json() devolve 'dados'.
    resposta = Mock()
    resposta.json.return_value = dados
    return resposta

def resposta_sucesso(valor):
    # Resposta falsa de sucesso da ExchangeRate-API.
    return resposta_falsa({"result": "success", "conversion_result": valor})

def executar(funcao, entradas, *args):
    """Roda uma funcao simulando o teclado.

    'entradas' e a lista do que o usuario "digita", na ordem.
    Retorna (o que a funcao devolveu, tudo o que ela imprimiu na tela).
    """
    saida = io.StringIO()
    with patch("builtins.input", side_effect=entradas), redirect_stdout(saida):
        retorno = funcao(*args)
    return retorno, saida.getvalue()

class TesteBase(unittest.TestCase):
    # Base que coloca uma chave falsa, para nao depender do seu .env.

    def setUp(self):
        patcher = patch.object(conversor, "API_KEY", "chave-teste")
        patcher.start()
        self.addCleanup(patcher.stop)

# pedir_moeda()

class TestPedirMoeda(unittest.TestCase):

    def test_aceita_moedas_validas(self):
        for moeda in ["BRL", "USD", "EUR"]:
            with self.subTest(moeda=moeda):
                resultado, _ = executar(conversor.pedir_moeda, [moeda], "Moeda: ")
                self.assertEqual(resultado, moeda)

    def test_aceita_minusculas_e_espacos(self):
        resultado, _ = executar(conversor.pedir_moeda, ["  usd "], "Moeda: ")
        self.assertEqual(resultado, "USD")

    def test_rejeita_moedas_invalidas_e_pergunta_de_novo(self):
        for invalida in ["XYZ", "", "REAL", "US", "123"]:
            with self.subTest(entrada=invalida):
                resultado, saida = executar(
                    conversor.pedir_moeda, [invalida, "EUR"], "Moeda: "
                )
                self.assertEqual(resultado, "EUR")
                self.assertIn("Moeda invalida", saida)

# pedir_valor()

class TestPedirValor(unittest.TestCase):

    def test_aceita_numeros_validos(self):
        casos = [
            ("10", 10.0),
            ("10.5", 10.5),
            ("10,5", 10.5),   # virgula como separador decimal
            (" 7 ", 7.0),
            ("0", 0.0),
            ("0,01", 0.01),
        ]
        for digitado, esperado in casos:
            with self.subTest(digitado=digitado):
                resultado, saida = executar(conversor.pedir_valor, [digitado])
                self.assertEqual(resultado, esperado)
                self.assertEqual(saida, "")

    def test_rejeita_textos_que_nao_sao_numeros(self):
        for texto in ["abc", "", "10a", "--5", "1,2,3", "R$10"]:
            with self.subTest(texto=texto):
                resultado, saida = executar(conversor.pedir_valor, [texto, "1"])
                self.assertEqual(resultado, 1.0)
                self.assertIn("Valor invalido", saida)

    def test_rejeita_valores_negativos(self):
        for negativo in ["-3", "-0,01", "-1000"]:
            with self.subTest(negativo=negativo):
                resultado, saida = executar(conversor.pedir_valor, [negativo, "4"])
                self.assertEqual(resultado, 4.0)
                self.assertIn("negativo", saida)

    def test_rejeita_nan_e_infinito(self):
        # float() aceita "nan" e "inf" como numeros, mas nao servem para converter
        resultado, saida = executar(
            conversor.pedir_valor, ["nan", "inf", "-inf", "2"]
        )
        self.assertEqual(resultado, 2.0)
        self.assertIn("Valor invalido", saida)

# converter() - a API e simulada (mock)

class TestConverter(TesteBase):

    @patch("conversor.requests.get")
    def test_retorna_o_resultado_da_api(self, mock_get):
        mock_get.return_value = resposta_sucesso(50.0)
        self.assertEqual(conversor.converter(10, "USD", "BRL"), 50.0)

    @patch("conversor.requests.get")
    def test_valor_zero(self, mock_get):
        mock_get.return_value = resposta_sucesso(0.0)
        self.assertEqual(conversor.converter(0, "USD", "BRL"), 0.0)

    @patch("conversor.requests.get")
    def test_monta_a_url_corretamente(self, mock_get):
        mock_get.return_value = resposta_sucesso(1.0)

        conversor.converter(10.5, "USD", "BRL")

        mock_get.assert_called_once()
        url = mock_get.call_args[0][0]
        self.assertEqual(
            url,
            "https://v6.exchangerate-api.com/v6/chave-teste/pair/USD/BRL/10.5",
        )

    @patch("conversor.requests.get")
    def test_usa_timeout_na_requisicao(self, mock_get):
        mock_get.return_value = resposta_sucesso(1.0)
        conversor.converter(1, "USD", "BRL")
        self.assertEqual(mock_get.call_args.kwargs.get("timeout"), 10)

    @patch("conversor.requests.get")
    def test_erro_retornado_pela_api(self, mock_get):
        mock_get.return_value = resposta_falsa(
            {"result": "error", "error-type": "invalid-key"}
        )
        saida = io.StringIO()
        with redirect_stdout(saida):
            resultado = conversor.converter(10, "USD", "BRL")

        self.assertIsNone(resultado)
        self.assertIn("invalid-key", saida.getvalue())

    @patch("conversor.requests.get")
    def test_resposta_sem_campo_result(self, mock_get):
        mock_get.return_value = resposta_falsa({})
        saida = io.StringIO()
        with redirect_stdout(saida):
            resultado = conversor.converter(10, "USD", "BRL")

        self.assertIsNone(resultado)
        self.assertIn("A API retornou um erro", saida.getvalue())

    @patch("conversor.requests.get")
    def test_falhas_de_rede_retornam_none(self, mock_get):
        erros = [
            requests.exceptions.ConnectionError(),
            requests.exceptions.Timeout(),
        ]
        for erro in erros:
            with self.subTest(erro=type(erro).__name__):
                mock_get.side_effect = erro
                saida = io.StringIO()
                with redirect_stdout(saida):
                    resultado = conversor.converter(10, "USD", "BRL")

                self.assertIsNone(resultado)
                self.assertIn("Erro de conexao", saida.getvalue())

    @patch("conversor.requests.get")
    def test_resposta_que_nao_e_json(self, mock_get):
        resposta = Mock()
        resposta.json.side_effect = requests.exceptions.JSONDecodeError("erro", "", 0)
        mock_get.return_value = resposta

        saida = io.StringIO()
        with redirect_stdout(saida):
            resultado = conversor.converter(10, "USD", "BRL")

        self.assertIsNone(resultado)

# main() - interface completa (teclado e API simulados)

class TestMain(TesteBase):
    # Executa o main() com as entradas dadas e devolve o texto impresso.

    def rodar(self, entradas):
        # Executa o main() com as entradas dadas e devolve o texto impresso.
        _, saida = executar(conversor.main, entradas)
        return saida

    @patch("conversor.requests.get")
    def test_fluxo_completo_com_sucesso(self, mock_get):
        mock_get.return_value = resposta_sucesso(50.0)

        saida = self.rodar(["USD", "BRL", "10", "n"])

        self.assertIn("=== Conversor de moedas ===", saida)
        self.assertIn("Moedas disponiveis: BRL, USD, EUR", saida)
        self.assertIn("Resultado: 10.00 USD = 50.00 BRL", saida)
        self.assertIn("Obrigado por usar o conversor!", saida)

    @patch("conversor.requests.get")
    def test_formatacao_e_arredondamento_do_resultado(self, mock_get):
        casos = [
            # (valor digitado, retorno da API, linha esperada na tela)
            ("10", 50.0, "10.00 USD = 50.00 BRL"),
            ("10,5", 52.5, "10.50 USD = 52.50 BRL"),
            ("3", 18.3333333, "3.00 USD = 18.33 BRL"),
            ("1000", 1234.5678, "1000.00 USD = 1234.57 BRL"),
            ("0", 0.0, "0.00 USD = 0.00 BRL"),
        ]
        for digitado, retorno_api, esperado in casos:
            with self.subTest(digitado=digitado):
                mock_get.return_value = resposta_sucesso(retorno_api)
                saida = self.rodar(["USD", "BRL", digitado, "n"])
                self.assertIn(f"Resultado: {esperado}", saida)

    @patch("conversor.requests.get")
    def test_envia_as_moedas_escolhidas_para_a_api(self, mock_get):
        mock_get.return_value = resposta_sucesso(11.0)

        self.rodar(["eur", "usd", "2", "n"])  # minusculas tambem funcionam

        url = mock_get.call_args[0][0]
        self.assertTrue(url.endswith("/pair/EUR/USD/2.0"))

    @patch("conversor.requests.get")
    def test_mesma_moeda_de_origem_e_destino(self, mock_get):
        mock_get.return_value = resposta_sucesso(5.0)
        saida = self.rodar(["BRL", "BRL", "5", "n"])
        self.assertIn("Resultado: 5.00 BRL = 5.00 BRL", saida)

    @patch("conversor.requests.get")
    def test_varias_conversoes_seguidas(self, mock_get):
        mock_get.side_effect = [resposta_sucesso(50.0), resposta_sucesso(11.0)]

        saida = self.rodar(["USD", "BRL", "10", "s", "EUR", "BRL", "2", "n"])

        self.assertEqual(mock_get.call_count, 2)
        self.assertIn("Resultado: 10.00 USD = 50.00 BRL", saida)
        self.assertIn("Resultado: 2.00 EUR = 11.00 BRL", saida)

    @patch("conversor.requests.get")
    def test_resposta_S_maiuscula_tambem_continua(self, mock_get):
        mock_get.return_value = resposta_sucesso(1.0)
        self.rodar(["USD", "BRL", "1", "S", "USD", "BRL", "1", "n"])
        self.assertEqual(mock_get.call_count, 2)

    @patch("conversor.requests.get")
    def test_qualquer_resposta_diferente_de_s_encerra(self, mock_get):
        for resposta in ["n", "N", "", "talvez", "sim"]:
            with self.subTest(resposta=resposta):
                mock_get.reset_mock()
                mock_get.return_value = resposta_sucesso(1.0)

                saida = self.rodar(["USD", "BRL", "1", resposta])

                self.assertEqual(mock_get.call_count, 1)
                self.assertIn("Obrigado por usar o conversor!", saida)

    @patch("conversor.requests.get")
    def test_entradas_invalidas_no_meio_do_fluxo(self, mock_get):
        mock_get.return_value = resposta_sucesso(50.0)

        saida = self.rodar(["XYZ", "USD", "BRL", "abc", "-5", "10", "n"])

        self.assertIn("Moeda invalida", saida)
        self.assertIn("Valor invalido", saida)
        self.assertIn("negativo", saida)
        self.assertIn("Resultado: 10.00 USD = 50.00 BRL", saida)
        self.assertEqual(mock_get.call_count, 1)  # so consulta a API com dados validos

    @patch("conversor.requests.get")
    def test_sem_chave_da_api_encerra_sem_pedir_dados(self, mock_get):
        for chave in [None, ""]:
            with self.subTest(chave=chave):
                with patch.object(conversor, "API_KEY", chave):
                    # lista vazia: se o programa chamar input(), o teste falha
                    saida = self.rodar([])

                self.assertIn("Chave da API nao encontrada", saida)
                mock_get.assert_not_called()

    @patch("conversor.requests.get")
    def test_falha_de_conexao_nao_mostra_resultado(self, mock_get):
        mock_get.side_effect = requests.exceptions.ConnectionError()

        saida = self.rodar(["USD", "BRL", "10", "n"])

        self.assertIn("Erro de conexao", saida)
        self.assertNotIn("Resultado:", saida)
        self.assertIn("Obrigado por usar o conversor!", saida)

    @patch("conversor.requests.get")
    def test_erro_da_api_nao_mostra_resultado(self, mock_get):
        mock_get.return_value = resposta_falsa(
            {"result": "error", "error-type": "quota-reached"}
        )

        saida = self.rodar(["USD", "BRL", "10", "n"])

        self.assertIn("quota-reached", saida)
        self.assertNotIn("Resultado:", saida)

    @patch("conversor.requests.get")
    def test_pode_tentar_de_novo_depois_de_um_erro(self, mock_get):
        mock_get.side_effect = [
            requests.exceptions.ConnectionError(),
            resposta_sucesso(50.0),
        ]

        saida = self.rodar(["USD", "BRL", "10", "s", "USD", "BRL", "10", "n"])

        self.assertIn("Erro de conexao", saida)
        self.assertIn("Resultado: 10.00 USD = 50.00 BRL", saida)

# Testes com a API REAL (opcionais)
#
# Gastam algumas requisicoes do seu plano. Para rodar:
#   Windows (PowerShell):  $env:RODAR_TESTES_REAIS="1"; python -m unittest -v
#   Linux/Mac:             RODAR_TESTES_REAIS=1 python -m unittest -v

@unittest.skipUnless(
    os.getenv("RODAR_TESTES_REAIS") == "1" and conversor.API_KEY,
    "Testes com a API real desativados "
    "(defina RODAR_TESTES_REAIS=1 e configure a API_KEY no .env).",
)
class TestAPIReal(unittest.TestCase):

    def test_mesma_moeda_retorna_o_mesmo_valor(self):
        self.assertAlmostEqual(conversor.converter(100, "BRL", "BRL"), 100, places=2)

    def test_cotacoes_sao_numeros_positivos(self):
        for moeda in ["USD", "EUR"]:
            with self.subTest(moeda=moeda):
                resultado = conversor.converter(1, moeda, "BRL")
                self.assertIsNotNone(resultado)
                self.assertGreater(resultado, 0)

    def test_conversao_e_proporcional_ao_valor(self):
        um = conversor.converter(1, "USD", "BRL")
        dez = conversor.converter(10, "USD", "BRL")
        self.assertAlmostEqual(dez, um * 10, delta=0.05)

    def test_ida_e_volta_retorna_aproximadamente_o_mesmo_valor(self):
        ida = conversor.converter(1, "USD", "BRL")
        volta = conversor.converter(1, "BRL", "USD")
        self.assertAlmostEqual(ida * volta, 1, delta=0.01)

    def test_chave_invalida_e_tratada(self):
        with patch.object(conversor, "API_KEY", "chave-invalida"):
            with redirect_stdout(io.StringIO()):
                resultado = conversor.converter(1, "USD", "BRL")
        self.assertIsNone(resultado)

if __name__ == "__main__":
    unittest.main()