# MCP Status Checker Skill

## Descrição

Verifica quais servidores MCP (Model Context Protocol) estão configurados e o status de cada um.

## Como Usar

Quando o usuário perguntar sobre MCPs ativos, execute:

### Passo 1: Ler configuração MCP

Leia o arquivo `~/.nanobot/mcp.json` (ou `bots.json`) para listar os MCPs configurados.

### Passo 2: Verificar saúde de cada MCP

Para cada MCP configurado:
- **HTTP MCPs**: Tente fazer request para o endpoint de health check
- **Command MCPs**: Verifique se o processo está rodando

### Passo 3: Reportar status

Apresente um relatório com:
- Nome do MCP
- Tipo (http/command)
- Status (✅ ativo / ❌ inativo)
- Descrição
- Endpoint/comando

## Formato de Saída

```
# MCP Servers Status

## Configurados: 3

### 1. Supermemory ✅
- **Tipo**: HTTP
- **URL**: http://localhost:3000
- **Descrição**: Persistent memory with semantic search
- **Status**: Ativo e respondendo

### 2. Exa Search ❌
- **Tipo**: Command
- **Comando**: npx -y @modelcontextprotocol/server-exa
- **Descrição**: Web search via Exa AI
- **Status**: Não iniciado ou sem API key

### 3. Filesystem ✅
- **Tipo**: Command
- **Comando**: npx -y @modelcontextprotocol/server-filesystem
- **Descrição**: File system operations
- **Status**: Rodando
```

## Implementação

### Para HTTP MCPs:

```python
import httpx

async def check_http_mcp(url: str, health_endpoint: str = "/health") -> bool:
    """Check if HTTP MCP is responding."""
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            response = await client.get(f"{url}{health_endpoint}")
            return response.status_code == 200
    except Exception:
        return False
```

### Para Command MCPs:

```python
import psutil
import subprocess

def check_command_mcp(command: str, args: list[str]) -> bool:
    """Check if command MCP process is running."""
    # Check if process with this command is running
    for proc in psutil.process_iter(['cmdline']):
        try:
            cmdline = proc.info['cmdline']
            if cmdline and command in ' '.join(cmdline):
                return True
        except:
            continue
    return False
```

## Exemplo de Uso pelo Usuário

```
Usuário: "Quais MCPs estão ativos?"
Usuário: "Status dos MCP servers"
Usuário: "Verifica se supermemory está rodando"
```

## Arquivos de Configuração

O status é baseado em:
- `~/.nanobot/mcp.json` - Configurações MCP
- `~/.nanobot/bots.json` - Configuração dos bots e quais MCPs usam

## Notas

- Alguns MCPs podem estar configurados mas não ativos
- MCPs HTTP dependem de servidor externo estar rodando
- MCPs Command são iniciados automaticamente pelo nanobot
