#  Bot de Xadrez para Chess.com

Bot automatizado em Python para jogar xadrez online no Chess.com, desenvolvido como trabalho acadêmico.

##  Índice

- [Características](#características)
- [Pré-requisitos](#pré-requisitos)
- [Instalação](#instalação)
- [Configuração](#configuração)
- [Como Usar](#como-usar)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Conceitos Aprendidos](#conceitos-aprendidos)
- [Avisos Importantes](#avisos-importantes)

##  Características

- ✅ Login automático no Chess.com
- ✅ Integração com Stockfish (engine de xadrez)
- ✅ Leitura automática do tabuleiro
- ✅ Cálculo e execução de movimentos
- ✅ Modo teste local (jogar no terminal)
- ✅ Documentação completa do código

##  Pré-requisitos

### Software Necessário

1. **Python 3.8+** 
   - Download: https://www.python.org/downloads/

2. **Google Chrome** 
   - Download: https://www.google.com/chrome/

3. **ChromeDriver** (gerenciado automaticamente pelo webdriver-manager)

4. **Stockfish** (opcional, mas recomendado)
   - Download: https://stockfishchess.org/download/
   - Extraia e anote o caminho do executável

### Conta no Chess.com

Você precisará de uma conta gratuita em https://www.chess.com

##  Instalação

### Passo 1: Clone ou baixe este projeto

```bash
# Se usar Git
git clone <seu-repositorio>
cd chess-bot

# Ou extraia o ZIP baixado
```

### Passo 2: Crie um ambiente virtual (recomendado)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### Passo 3: Instale as dependências

```bash
pip install -r requirements.txt
```

### Instalação das dependencias codigo unico

```bash
pip install python-chess selenium webdriver-manager
```

### Passo 4: Instale o Stockfish

#### Windows
1. Baixe o ZIP em https://stockfishchess.org/download/
2. Extraia para `C:\stockfish\`
3. O executável estará em `C:\stockfish\stockfish-windows-x86-64-avx2.exe`

#### Linux
```bash
sudo apt-get install stockfish
# Ou compile do código-fonte
```

#### Mac
```bash
brew install stockfish
```

##  Configuração

### 1. Configure suas credenciais

Edite o arquivo `chess_bot.py` nas linhas:

```python
USERNAME = "seu_usuario"  # Seu usuário do Chess.com
PASSWORD = "sua_senha"    # Sua senha do Chess.com
```

### 2. Configure o caminho do Stockfish

```python
# Windows
STOCKFISH_PATH = r"C:\stockfish\stockfish-windows-x86-64-avx2.exe"

# Linux
STOCKFISH_PATH = "/usr/games/stockfish"

# Mac
STOCKFISH_PATH = "/usr/local/bin/stockfish"
```

##  Como Usar

### Modo 1: Teste Local (Recomendado para começar)

Primeiro teste o bot localmente no terminal:

```bash
python simple_chess_bot.py
```

Este modo permite:
- Jogar contra o bot sem internet
- Testar se o Stockfish está funcionando
- Entender a lógica do jogo
- Aprender notação de xadrez

### Modo 2: Bot Online (Chess.com)

** ATENÇÃO: Leia os [Avisos Importantes](#avisos-importantes) antes!**

```bash
python chess_bot.py
```

O bot irá:
1. Abrir o Chrome
2. Fazer login no Chess.com
3. Iniciar uma partida
4. Jogar automaticamente

##  Estrutura do Projeto

```
chess-bot/
│
├── chess_bot.py              # Bot principal (Chess.com)
├── simple_chess_bot.py       # Versão de teste local
├── requirements.txt          # Dependências
├── README.md                 # Este arquivo
│
└── docs/                     # (opcional) Documentação adicional
    ├── relatorio.md          # Relatório do trabalho
    └── apresentacao.pptx     # Slides
```

##  Conceitos Aprendidos

### 1. Automação Web com Selenium
- Controle programático de navegadores
- Localização e interação com elementos HTML
- Waits e sincronização

### 2. Lógica de Jogos
- Representação de tabuleiros
- Validação de movimentos legais
- Estados de jogo (xeque, mate, empate)

### 3. Integração com Engines
- Comunicação via UCI (Universal Chess Interface)
- Análise de posições
- Cálculo de melhores movimentos

### 4. Bibliotecas Python
- `python-chess`: Manipulação de tabuleiros e regras
- `selenium`: Automação web
- `chess.engine`: Interface com Stockfish

##  Avisos Importantes

### Sobre o Uso em Chess.com

1. **Termos de Serviço**: O Chess.com proíbe o uso de bots e assistência computacional em partidas ranqueadas. Usar este bot pode resultar em:
   - Banimento permanente da conta
   - Perda de rating
   - Outras penalidades

2. **Propósito Educacional**: Este código foi desenvolvido exclusivamente para:
   - Aprendizado de programação
   - Estudo de IA aplicada a jogos
   - Compreensão de automação web
   - Trabalho acadêmico

3. **Uso Ético Recomendado**:
   - ✅ Teste local com `simple_chess_bot.py`
   - ✅ Análise de partidas já finalizadas
   - ✅ Desenvolvimento de novas features
   - ❌ NÃO use em partidas ranqueadas
   - ❌ NÃO use para trapacear

### Alternativas Legítimas

Para jogar com engines sem violar regras:
- **Lichess**: Permite bots em área específica (https://lichess.org/api)
- **Modo análise**: Use engines para estudar suas partidas
- **Partidas locais**: Jogue offline com o `simple_chess_bot.py`

##  Como Funciona

### Fluxo Principal

```
1. Login no Chess.com
   ↓
2. Acessa página de jogar
   ↓
3. Loop de jogo:
   ├─ Lê estado do tabuleiro
   ├─ Calcula melhor movimento (Stockfish)
   ├─ Executa movimento
   ├─ Aguarda oponente
   └─ Repete até fim de jogo
   ↓
4. Mostra resultado
```

### Componentes Principais

**ChessComBot**: Classe principal que gerencia:
- `setup_browser()`: Inicializa Selenium
- `login()`: Autentica no site
- `setup_engine()`: Carrega Stockfish
- `get_board_state()`: Lê posição atual
- `calculate_best_move()`: Usa engine para decidir
- `make_move()`: Clica nas casas corretas
- `play_game()`: Loop principal

##  Troubleshooting

### Erro: "ChromeDriver not found"
```bash
pip install webdriver-manager --upgrade
```

### Erro: "Engine not found"
Verifique se o caminho do Stockfish está correto:
```python
# Teste no Python
from pathlib import Path
print(Path("SEU_CAMINHO_AQUI").exists())
```

### Bot não reconhece movimentos
- Verifique se o Chess.com mudou o layout
- Pode ser necessário atualizar os seletores CSS

### Login falha
- Verifique credenciais
- Chess.com pode ter CAPTCHA (resolver manualmente)

##  Recursos para Estudo

- [Documentação python-chess](https://python-chess.readthedocs.io/)
- [Selenium Documentation](https://selenium-python.readthedocs.io/)
- [Stockfish UCI Protocol](https://www.chessprogramming.org/UCI)
- [Chess.com API](https://www.chess.com/news/view/published-data-api)

##  Sugestões para o Trabalho

### Possíveis Melhorias

1. **Níveis de dificuldade**: Limitar tempo de pensamento
2. **Abertura preparada**: Database de aberturas
3. **Análise pós-jogo**: Salvar e analisar PGN
4. **Interface gráfica**: PyQt ou Tkinter
5. **Machine Learning**: Treinar rede neural própria

### Tópicos para Apresentação

- Arquitetura do sistema
- Desafios técnicos enfrentados
- Algoritmos de busca em jogos
- Ética em IA e jogos
- Comparação com outras implementações

##  Licença

Este projeto é para fins educacionais. Use responsavelmente.

##  Autor

Desenvolvido como trabalho acadêmico. 
por PZW...

---

**Lembre-se**: Programação é sobre aprender e criar. Use este conhecimento de forma ética! ♟️
