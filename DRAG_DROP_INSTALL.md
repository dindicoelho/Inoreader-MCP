# 🚀 Instalação Drag & Drop

## Opção 1: Instalador Automático (Recomendado)

**Simplesmente execute:**
```bash
python3 install_inoreader_mcp.py
```

O instalador irá:
- ✅ Instalar dependências automaticamente
- ✅ Solicitar suas credenciais do Inoreader
- ✅ Configurar o Claude Desktop automaticamente
- ✅ Deixar tudo pronto para uso!

## Opção 2: Drag & Drop (Se o Claude suportar)

1. Arraste o arquivo `inoreader-mcp.dxt` para o Claude Desktop
2. Siga as instruções na tela

## Opção 3: Manual (Fallback)

Se nenhuma das opções acima funcionar:

1. Copie `claude_config_example.json`
2. Atualize com suas credenciais
3. Substitua o arquivo de config do Claude Desktop

## 🔐 Credenciais do Inoreader

Para obter credenciais:
1. Acesse https://www.inoreader.com/developers/
2. Clique "Create new application"
3. Escolha "Web Application"
4. Copie App ID e App Key

## ✅ Teste da Instalação

Após instalar, teste no Claude Desktop:
```
"List my unread articles"
"Search for articles about technology"
"Show my feed statistics"
```

---

**💡 Dica:** Use o `install_inoreader_mcp.py` - é a forma mais rápida e confiável!