# Conversor de Moedas

Projeto desenvolvido para a atividade **Parada Obrigatória 1** da disciplina **Alta Qualidade de Software**.

## Quadro Scrum no Trello

Na proposta da atividade, foi solitado o uso do quadro seguindo as regras da metologia ágil Scrum.   
A partir disso foi criado o quadro "Agile Docs & Code Sprint" na plataforma Trello contendo os blocos com as regras do Scrum: Backlog, To Do, In progress e Done.

#### Estarei anexando o link do quadro no Trello para possível visualização: [Agile Docs & Code Sprint](https://trello.com/invite/b/6ab43843250e9de3fa76702f/ATTI353585188eb236a3f293ed2b77bd99cd9FA2131A/agile-docs-code-sprint).

## Objetivo do projeto

A atividade simula uma sprint de desenvolvimento no framework Scrum, tendo como produto um sistema simples de conversão de moedas. Os objetivos são:

- Realizar uma atividade que simula uma sprint de desenvolvimento no framework Scrum;
- Criar a documentação de software;
- Implementar testes unitários para o sistema de conversão de moedas;
- Ao final, refletir sobre o processo de desenvolvimento usando o framework Scrum.

## Sobre o conversor

O `conversor.py` é um programa de terminal que converte valores entre **BRL** (real), **USD** (dólar americano) e **EUR** (euro). As cotações não são fixas: a cada conversão, o programa consulta a API da [ExchangeRate-API](https://www.exchangerate-api.com).

## Estrutura do projeto

```text
.
├── conversor.py        # Programa principal
├── TestConversor.py   # Testes unitários
├── Documentação.md     # Documentação técnica detalhada
├── .env                # Chave da API (não deve ser compartilhado)
└── README.md
```

## Requisitos

- Python 3.8 ou superior
- Bibliotecas `requests` (versão 2.27 ou superior) e `python-dotenv`
- Uma chave de API da ExchangeRate-API (há plano gratuito)
- Conexão com a internet para usar o conversor

## Configuração

1. Instale as dependências:

```bash
pip install requests python-dotenv
```

2. Crie um arquivo `.env` na pasta do projeto com a sua chave:

```text
API_KEY=sua_chave_aqui
```

> O arquivo `.env` contém uma informação secreta. Não o envie para repositórios públicos (se usar Git, adicione `.env` ao `.gitignore`).

## Como executar o conversor

Na pasta do projeto, execute:

```bash
python conversor.py
```

## Resumo do código

O `conversor.py` é dividido em pequenas funções:

| Elemento | Função |
| --- | --- |
| `API_KEY` | Chave da API, lida do arquivo `.env`. |
| `MOEDAS` | Lista de moedas aceitas (BRL, USD e EUR). |
| `pedir_moeda()` | Pede uma moeda ao usuário e repete a pergunta até receber uma válida. |
| `pedir_valor()` | Pede um valor numérico (aceita ponto ou vírgula) e rejeita textos, valores negativos, `nan` e `inf`. |
| `converter()` | Consulta a API e devolve o valor convertido, ou `None` se houver erro de conexão ou erro retornado pela API. |
| `main()` | Controla o fluxo do programa: coleta os dados, exibe o resultado e pergunta se o usuário quer converter novamente. |

A conversão em si é feita pela API. O programa se encarrega de validar as entradas, tratar os erros e exibir o resultado com duas casas decimais.

Para mais detalhes (tratamento de erros, limitações, endpoint utilizado), consulte a [documentação técnica](documentacao.md).

## Testes unitários

Os testes ficam no arquivo `test_conversor.py` e usam o módulo `unittest`, que já vem com o Python. Não é preciso instalar nada além das dependências do projeto.

### Como executar

Na pasta do projeto (onde estão `conversor.py` e `test_conversor.py`), execute:

```bash
python -m unittest -v
```

A opção `-v` mostra o resultado de cada teste individualmente. Para rodar apenas um grupo de testes, informe o nome da classe:

```bash
python -m unittest test_conversor.TestConverter -v
```

### O que é testado

| Classe de teste | O que verifica |
| --- | --- |
| `TestPedirMoeda` | Moedas válidas, letras minúsculas, espaços e moedas inválidas. |
| `TestPedirValor` | Números válidos (ponto e vírgula), textos, valores negativos, `nan` e `inf`. |
| `TestConverter` | Resultado devolvido pela API, URL montada corretamente, timeout, erro da API, resposta inválida e falhas de rede. |
| `TestMain` | Fluxo completo da interface: mensagens, formatação do resultado, várias conversões seguidas, entradas inválidas, ausência de chave e recuperação após erros. |
| `TestAPIReal` | Consistência das cotações com a API de verdade (opcional, veja abaixo). |

Nos testes normais, o teclado (`input`) e a API (`requests.get`) são **simulados** com `unittest.mock`. Por isso eles rodam rápido, não precisam de internet e não gastam requisições do seu plano.

### Testes com a API real (opcionais)

A classe `TestAPIReal` faz requisições de verdade à API para verificar se as cotações são consistentes (por exemplo, BRL para BRL devolve o mesmo valor e a conversão de ida e volta se cancela). Como consomem requisições do plano, ficam **desativados por padrão** e são ignorados na execução normal.

Para ativá-los, defina a variável `RODAR_TESTES_REAIS` antes de rodar:

```bash
# Windows (PowerShell)
$env:RODAR_TESTES_REAIS="1"; python -m unittest -v

# Linux / macOS
RODAR_TESTES_REAIS=1 python -m unittest -v
```

Para isso, o arquivo `.env` precisa conter uma chave de API válida.

### Resultado esperado

Sem os testes reais, a execução termina com algo como:

```text
Ran 32 tests in 0.0Xs

OK (skipped=5)
```

Os 5 testes ignorados (`skipped`) são os da API real. Com eles ativados, todos os 32 testes são executados.