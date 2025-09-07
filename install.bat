@echo off
echo 🚀 Instalador Automático do Inoreader MCP (Windows)
echo =================================================

:: Verifica se Python está instalado
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python não encontrado! Instale Python 3.8+ primeiro.
    echo 📖 Download: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo ✅ Python encontrado!

:: Executa o instalador Python
python install_inoreader_mcp.py

echo.
echo 🎉 Instalação concluída! Reinicie o Claude Desktop.
pause