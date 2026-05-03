#!/bin/bash
# Script de instalação para Chess.com Bot Autônomo V3

echo "============================================"
echo "  Chess.com Bot Autônomo - Instalação"
echo "============================================"
echo ""

# Verifica Python
python_version=$(python3 --version 2>/dev/null || python --version 2>/dev/null)
if [ -z "$python_version" ]; then
    echo "❌ Python não encontrado! Instale o Python 3.8+"
    exit 1
fi
echo "✅ $python_version"

# Instala dependências
echo ""
echo "[*] Instalando dependências..."
pip install selenium chess 2>/dev/null || pip3 install selenium chess 2>/dev/null

# Verifica Chrome
if command -v google-chrome &> /dev/null; then
    echo "✅ Google Chrome encontrado"
elif command -v chromium &> /dev/null; then
    echo "✅ Chromium encontrado"
elif command -v chromium-browser &> /dev/null; then
    echo "✅ Chromium encontrado"
else
    echo "⚠️  Chrome/Chromium não encontrado"
    echo "   Baixe em: https://www.google.com/chrome/"
fi

# Verifica ChromeDriver
echo ""
echo "[*] Verificando ChromeDriver..."
if command -v chromedriver &> /dev/null; then
    echo "✅ ChromeDriver encontrado"
else
    echo "ℹ️  ChromeDriver será baixado automaticamente pelo Selenium"
fi

# Verifica Stockfish (opcional)
echo ""
echo "[*] Verificando Stockfish..."
if command -v stockfish &> /dev/null; then
    echo "✅ Stockfish encontrado no PATH"
    echo "   Caminho: $(which stockfish)"
else
    echo "⚠️  Stockfish não encontrado"
    echo "   O bot funcionará com movimentos aleatórios"
    echo "   Para instalar:"
    echo "   - Ubuntu/Debian: sudo apt install stockfish"
    echo "   - Mac: brew install stockfish"
    echo "   - Windows: Baixe em https://stockfishchess.org/download/"
fi

echo ""
echo "============================================"
echo "  Instalação concluída!"
echo "============================================"
echo ""
echo "Próximos passos:"
echo "1. Edite o arquivo chess_bot_autonomo_v3.py"
echo "2. Configure USERNAME, PASSWORD e STOCKFISH_PATH"
echo "3. Execute: python chess_bot_autonomo_v3.py"
echo ""
