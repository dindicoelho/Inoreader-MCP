#!/usr/bin/env python3
"""
Instalador automático do Inoreader MCP
Drag & drop este arquivo no Claude Desktop ou execute diretamente
"""
import json
import os
import sys
from pathlib import Path
import subprocess
import getpass

def get_claude_config_path():
    """Detecta o caminho do arquivo de configuração do Claude Desktop"""
    if sys.platform == "darwin":  # macOS
        return Path.home() / "Library/Application Support/Claude/claude_desktop_config.json"
    elif sys.platform == "win32":  # Windows
        return Path(os.environ["APPDATA"]) / "Claude/claude_desktop_config.json"
    else:  # Linux
        return Path.home() / ".config/claude/claude_desktop_config.json"

def install_dependencies():
    """Instala as dependências Python necessárias"""
    print("📦 Instalando dependências Python...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "aiohttp>=3.9.0", "python-dotenv>=1.0.0"])
        print("✅ Dependências instaladas com sucesso!")
        return True
    except subprocess.CalledProcessError:
        print("❌ Erro ao instalar dependências. Verifique se o pip está instalado.")
        return False

def get_credentials():
    """Coleta credenciais do usuário"""
    print("\n🔐 Configuração das Credenciais do Inoreader")
    print("📖 Para obter credenciais: https://www.inoreader.com/developers/")
    print("   1. Crie uma nova aplicação")
    print("   2. Escolha 'Web Application'")
    print("   3. Copie App ID e App Key\n")
    
    app_id = input("🆔 Inoreader App ID: ").strip()
    app_key = input("🔑 Inoreader App Key: ").strip()
    username = input("👤 Seu email do Inoreader: ").strip()
    password = getpass.getpass("🔒 Sua senha do Inoreader: ")
    
    if not all([app_id, app_key, username, password]):
        print("❌ Todas as credenciais são obrigatórias!")
        return None
        
    return {
        "INOREADER_APP_ID": app_id,
        "INOREADER_APP_KEY": app_key,
        "INOREADER_USERNAME": username,
        "INOREADER_PASSWORD": password
    }

def update_claude_config(credentials):
    """Atualiza a configuração do Claude Desktop"""
    config_path = get_claude_config_path()
    current_dir = Path(__file__).parent.absolute()
    main_py_path = current_dir / "main.py"
    
    # Cria diretório se não existir
    config_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Carrega configuração existente ou cria nova
    if config_path.exists():
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
        except json.JSONDecodeError:
            config = {}
    else:
        config = {}
    
    # Adiciona configuração do Inoreader MCP
    if "mcpServers" not in config:
        config["mcpServers"] = {}
    
    config["mcpServers"]["inoreader-mcp"] = {
        "command": "python3",
        "args": [str(main_py_path)],
        "env": credentials
    }
    
    # Salva configuração
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"✅ Configuração salva em: {config_path}")
    return True

def main():
    print("🚀 Instalador Automático do Inoreader MCP")
    print("=" * 50)
    
    # Verificar se estamos no diretório correto
    current_dir = Path(__file__).parent
    main_py = current_dir / "main.py"
    
    if not main_py.exists():
        print(f"❌ Erro: main.py não encontrado em {current_dir}")
        print("   Execute este instalador na pasta do projeto Inoreader MCP")
        sys.exit(1)
    
    # 1. Instalar dependências
    if not install_dependencies():
        sys.exit(1)
    
    # 2. Coletar credenciais
    credentials = get_credentials()
    if not credentials:
        sys.exit(1)
    
    # 3. Atualizar configuração do Claude
    if not update_claude_config(credentials):
        sys.exit(1)
    
    print("\n🎉 Instalação Concluída!")
    print("=" * 30)
    print("📋 Próximos passos:")
    print("1. Reinicie o Claude Desktop")
    print("2. Teste com: 'List my unread articles'")
    print("3. Experimente: 'Search for articles about technology'")
    print("\n✨ Aproveite seu Inoreader MCP integrado!")

if __name__ == "__main__":
    main()