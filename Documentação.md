# Documentação do conversor de moedas
 
## 1. Objetivo
 
O programa `conversor.py` permite converter valores entre três moedas pré-definidas:
 
- BRL - Real brasileiro;
- USD - Dólar americano;
- EUR - Euro.
O conversor funciona no terminal e apresenta uma interface simples para que o usuário informe a moeda de origem, a moeda de destino e o valor desejado.
 
## 2. Como executar
 
Antes de executar, siga a configuração descrita no tópico 3 (instalação das dependências e criação do arquivo `.env`). Também é necessário ter conexão com a internet.
 
Abra o terminal na pasta do projeto e execute:
 
```bash
python conversor.py
```
 
O programa exibirá as moedas disponíveis e solicitará os dados da conversão.
Ao final de cada operação, o usuário pode escolher entre realizar uma nova conversão ou encerrar o programa.
 
## 3. Taxas utilizadas
 
As taxas de conversão são obtidas em tempo de execução pela API da [ExchangeRate-API](https://www.exchangerate-api.com). O programa não armazena taxas fixas: a cada conversão, ele consulta a API e usa o resultado retornado.
 
### Configuração
 
1. Instale as dependências:
```bash
pip install requests python-dotenv
```
 
2. Crie um arquivo `.env` na mesma pasta do `conversor.py` com a chave da API:
```text
API_KEY=sua_chave_aqui
```
 
O arquivo `.env` não deve ser compartilhado nem enviado a repositórios públicos.
 
### Como a consulta funciona
 
A função `converter()` faz uma requisição HTTP para o endpoint `pair` da API, informando a moeda de origem, a moeda de destino e o valor:
 
```text
https://v6.exchangerate-api.com/v6/{API_KEY}/pair/{origem}/{destino}/{valor}
```
 
A API devolve um JSON. O programa verifica se o campo `result` é `success` e, em caso positivo, usa o campo `conversion_result` como valor convertido.
 
### Tratamento de erros
 
- Se a chave `API_KEY` não for encontrada no `.env`, o programa avisa e encerra.
- Se houver falha de conexão, o programa exibe uma mensagem e permite tentar novamente.
- Se a API retornar erro (por exemplo, chave inválida ou limite de requisições excedido), o programa exibe o motivo informado pela API.
A frequência de atualização das cotações depende do plano contratado na ExchangeRate-API.
 
## 4. Funcionamento da conversão
 
O cálculo da conversão é feito pela própria API. O programa apenas envia o pedido e exibe a resposta:
 
1. O programa envia à API a moeda de origem, a moeda de destino e o valor digitado.
2. A API calcula a conversão com a cotação do momento e devolve o resultado no campo `conversion_result`.
3. O programa exibe o resultado formatado com duas casas decimais.
Por exemplo, considerando uma cotação de 1 USD = 5,00 BRL (valor ilustrativo):
 
```text
10 USD = 50,00 BRL
100 BRL = 20,00 USD
```
 
Os valores numéricos são tratados como `float`, e o arredondamento para duas casas decimais é feito apenas na exibição do resultado (`:.2f`). Para um conversor de uso simples isso é suficiente, mas não é recomendado para aplicações financeiras que exijam precisão exata.
 
## 5. Entrada e validações
 
- Os códigos das moedas não diferenciam letras maiúsculas de minúsculas.
- O valor pode ser digitado usando ponto ou vírgula como separador decimal.
- Moedas que não estão cadastradas são rejeitadas.
- Textos que não representam números são rejeitados.
- Valores negativos não são aceitos.
- O resultado é exibido sempre com duas casas decimais.
## 6. Organização do código
 
- `API_KEY`: chave da API, lida do arquivo `.env` por meio de `load_dotenv()` e `os.getenv()`.
- `MOEDAS`: lista com os códigos das moedas aceitas pelo programa.
- `pedir_moeda()`: solicita e valida uma moeda.
- `pedir_valor()`: solicita e valida um valor numérico.
- `converter()`: consulta a API e retorna o valor convertido (ou `None` em caso de erro).
- `main()`: controla a interface e o fluxo principal do programa.
## 7. Exemplo de uso
 
```text
=== Conversor de moedas ===
Moedas disponiveis: BRL, USD, EUR
Moeda de origem: USD
Moeda de destino: BRL
Digite o valor a converter: 10
Resultado: 10.00 USD = 50.00 BRL
Deseja fazer outra conversao? (s/n): n
Obrigado por usar o conversor!
```
 
Os valores do exemplo são ilustrativos: como as taxas vêm da API, o resultado real depende da cotação do momento.
 
## 8. Limitações conhecidas
 
- O programa depende de conexão com a internet. Sem ela, nenhuma conversão é realizada.
- É necessária uma chave de API válida no arquivo `.env`.
- O número de consultas é limitado pelo plano da ExchangeRate-API. Se o limite for excedido, a API retornará erro.
- Apenas as moedas listadas em `MOEDAS` (BRL, USD e EUR) são aceitas, embora a API suporte muitas outras.
- As cotações da API são de referência e podem diferir das praticadas por bancos e casas de câmbio.