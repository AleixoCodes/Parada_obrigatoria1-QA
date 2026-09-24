import os
import requests
from dotenv import load_dotenv

# Le o arquivo .env e pega a chave da API
load_dotenv()
API_KEY = os.getenv("API_KEY")

MOEDAS = ["BRL", "USD", "EUR"]

def pedir_moeda(mensagem):
   #Pede uma moeda ate o usuario digitar uma valida.
    while True:
        moeda = input(mensagem).strip().upper()
        if moeda in MOEDAS:
            return moeda
        print("Moeda invalida. Escolha uma das moedas disponiveis.")

def pedir_valor():
    #Pede um valor ate o usuario digitar um numero valido.
    while True:
        entrada = input("Digite o valor a converter: ").replace(",", ".")
        try:
            valor = float(entrada)
        except ValueError:
            print("Valor invalido. Digite apenas um numero.")
            continue

        if valor < 0:
            print("O valor nao pode ser negativo.")
            continue
        return valor

def converter(valor, origem, destino):
    #Pede a conversao para a API. Retorna o resultado ou None se der erro.
    url = f"https://v6.exchangerate-api.com/v6/{API_KEY}/pair/{origem}/{destino}/{valor}"

    try:
        resposta = requests.get(url, timeout=10)
        dados = resposta.json()
    except requests.RequestException:
        print("Erro de conexao. Verifique sua internet e tente novamente.")
        return None

    if dados["result"] != "success":
        print("A API retornou um erro:", dados.get("error-type"))
        return None

    return dados["conversion_result"]

def main():
    print("=== Conversor de moedas ===")

    if not API_KEY:
        print("Chave da API nao encontrada. Confira o arquivo .env.")
        return

    print("Moedas disponiveis:", ", ".join(MOEDAS))

    while True:
        origem = pedir_moeda("Moeda de origem: ")
        destino = pedir_moeda("Moeda de destino: ")
        valor = pedir_valor()

        resultado = converter(valor, origem, destino)
        if resultado is not None:
            print(f"Resultado: {valor:.2f} {origem} = {resultado:.2f} {destino}")

        continuar = input("Deseja fazer outra conversao? (s/n): ").strip().lower()
        if continuar != "s":
            print("Obrigado por usar o conversor!")
            break

main()