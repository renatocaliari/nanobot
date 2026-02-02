# Deploy Nanobot no Dokploy

**📌 Este guia é para o fork [renatocaliari/nanobot](https://github.com/renatocaliari/nanobot).** Para o projeto original, veja [HKUDS/nanobot](https://github.com/HKUDS/nanobot).

Este guia orienta você através do processo de deploy do **nanobot** usando **Docker Compose** no **Dokploy**.

> **⭐ Novidades neste fork:**
> - Suporte a **Z.AI** (GLM models a $0.11/M tokens)
> - Docker otimizado para **Dokploy**
> - Correções de segurança e bugs
>
> Veja [FORK_CHANGES.md](./FORK_CHANGES.md) para detalhes completos.

## 📋 Pré-requisitos

Antes de começar, certifique-se de ter:

- ✅ Servidor Dokploy configurado e rodando
- ✅ Conhecimento básico de Docker e Docker Compose
- ✅ API keys dos provedores (OpenRouter, Anthropic, etc.)

## 🚀 Passo 1: Preparar o Repositório

Se você ainda não tem o código com o Dockerfile:

```bash
# Clone o fork com suporte Docker e Z.AI
git clone https://github.com/renatocaliari/nanobot.git
cd nanobot

# Faça checkout do branch com Dockerfile
git checkout claude/add-dockerfile-uv-1i3Kt
```

## 📝 Passo 2: Configurar Variáveis de Ambiente

```bash
# Copie o arquivo de exemplo
cp .env.example .env

# Edite o arquivo .env com suas credenciais
nano .env
```

**Variáveis obrigatórias:**
- `NANOBOT_PROVIDERS__ZAI__API_KEY`: Sua chave da Z.AI (https://open.bigmodel.cn/usercenter/apikeys)
  - `NANOBOT_PROVIDERS__ZAI__API_BASE`: Endpoint da API Z.AI
    - Para **Z.AI Coding Plan** (recomendado): `https://api.z.ai/api/coding/paas/v4/`
    - Para **Zhipu AI padrão**: `https://open.bigmodel.cn/api/paas/v4/`
  - OU `NANOBOT_PROVIDERS__OPENROUTER__API_KEY`: Sua chave da OpenRouter (https://openrouter.ai/keys)

**Variáveis opcionais:**
- `NANOBOT_AGENTS__DEFAULTS__MODEL`: Modelo a usar (padrão: zai/glm-4.7)
- `NANOBOT_CHANNELS__TELEGRAM__TOKEN`: Token do bot Telegram (@BotFather)
- `NANOBOT_CHANNELS__TELEGRAM__ALLOW_FROM`: IDs de usuários permitidos
  - ⚠️ **IMPORTANTE**: Use formato JSON válido com aspas: `["123456789"]`
  - ❌ Errado: `[123456789]` (sem aspas)
  - ❌ Errado: `123456789` (sem colchetes)
  - ✅ Correto: `["123456789"]` ou `["123456789", "987654321"]`
- `NANOBOT_CHANNELS__WHATSAPP__ENABLED`: true/false para WhatsApp
- `NANOBOT_PORT`: Porta do gateway (padrão: 18790)

> **💡 Dica**: Para múltiplos usuários no Telegram, separe por vírgula dentro do array JSON: `["123456789", "987654321", "@usuario"]`

## 🐳 Passo 3: Deploy no Dokploy

### Opção A: Via GitHub Integration (Recomendado)

1. **Push para GitHub**

```bash
git add .
git commit -m "Add Docker configuration"
git push origin claude/add-dockerfile-uv-1i3Kt
```

2. **Criar Aplicação no Dokploy**

- Acesse o painel do Dokploy
- Clique em "Create Application"
- Selecione "Docker Compose"
- Configure:

```yaml
# Repository Configuration
Repository: https://github.com/pve/nanobot-ai.git
Branch: claude/add-dockerfile-uv-1i3Kt

# Build Configuration
Docker Compose Path: docker-compose.yml
Environment: .env

# Port Configuration
Port: 18790

# Domain (opcional)
Domain: nanobot.seudominio.com
```

3. **Deploy**

- Clique em "Deploy"
- Aguarde o build e deploy completarem

### Opção B: Via Docker Compose Direto

Se você prefere deploy manual:

1. **Acesse o servidor via SSH**

```bash
ssh seu-servidor
```

2. **Clone o repositório**

```bash
cd /opt/dokploy/apps
git clone https://github.com/pve/nanobot-ai.git nanobot
cd nanobot
git checkout claude/add-dockerfile-uv-1i3Kt
```

3. **Configure as variáveis**

```bash
cp .env.example .env
nano .env
```

4. **Inicie o container**

```bash
docker-compose up -d
```

## 🔧 Passo 4: Configurar o Nanobot

Após o container iniciar, você precisa configurar o nanobot:

```bash
# Execute o comando de onboard
docker-compose exec nanobot nanobot onboard

# Verifique o status
docker-compose exec nanobot nanobot status
```

Edite a configuração se necessário:

```bash
# Edite o config.json dentro do container
docker-compose exec nanobot nano /root/.nanobot/config.json
```

Exemplo de `config.json`:

```json
{
  "providers": {
    "openrouter": {
      "apiKey": "sk-or-v1-xxx"
    }
  },
  "agents": {
    "defaults": {
      "model": "anthropic/claude-opus-4-5"
    }
  },
  "webSearch": {
    "apiKey": "BSA-xxx"
  },
  "channels": {
    "telegram": {
      "enabled": true,
      "token": "SEU_BOT_TOKEN",
      "allowFrom": ["123456789"]
    }
  }
}
```

## 🔄 Passo 5: Reiniciar com Nova Configuração

```bash
# Reinicie o container para aplicar mudanças
docker-compose restart

# Verifique os logs
docker-compose logs -f nanobot
```

## ✅ Passo 6: Verificar Deploy

```bash
# Verifique se o container está rodando
docker-compose ps

# Teste o gateway
curl http://localhost:18790/health

# Verifique o status
docker-compose exec nanobot nanobot status
```

## 🌐 Configuração de Domínio (Opcional)

Se você configurou um domínio no Dokploy:

1. **Configure o DNS**

   - Adicione um registro A apontando para o IP do seu servidor
   - Ou configure CNAME para o domínio do Dokploy

2. **Configure o Reverse Proxy** (se necessário)

O Dokploy geralmente configura isso automaticamente.

## 📊 Monitoramento e Logs

```bash
# Ver logs em tempo real
docker-compose logs -f nanobot

# Ver últimos 100 logs
docker-compose logs --tail=100 nanobot

# Ver estatísticas do container
docker stats nanobot
```

## 🛠️ Troubleshooting

### Container não inicia

```bash
# Ver logs de erro
docker-compose logs nanobot

# Verifique se as portas estão em uso
netstat -tulpn | grep 18790
```

### Erro de permissão

```bash
# Ajuste permissões do volume
docker-compose down
sudo chown -R 999:999 /var/lib/docker/volumes/nanobot-config
docker-compose up -d
```

### API keys não funcionam

```bash
# Verifique se as variáveis estão setadas
docker-compose exec nanobot env | grep API

# Recrie o container com .env atualizado
docker-compose down
docker-compose up -d
```

## 🔄 Atualizar o Nanobot

```bash
# Pull das atualizações
git pull origin claude/add-dockerfile-uv-1i3Kt

# Rebuild e restart
docker-compose down
docker-compose build
docker-compose up -d
```

## 📱 Integração com Telegram/WhatsApp

Após configurar no `config.json`:

```bash
# Para Telegram
# O gateway já estará rodando, apenas envie mensagens para o bot

# Para WhatsApp
# Você precisará executar o login manualmente na primeira vez
docker-compose exec nanobot nanobot channels login
# Escaneie o QR code no WhatsApp
```

## 🔐 Segurança

- **Nunca** commite o arquivo `.env` no git
- Use secrets do Dokploy quando possível
- Mantenha suas API keys seguras
- Configure firewall se necessário

## 📚 Recursos Adicionais

- [Nanobot Documentation](https://github.com/HKUDS/nanobot)
- [Dokploy Documentation](https://dokploy.com/docs)
- [Docker Compose Reference](https://docs.docker.com/compose/)

## 💡 Dicas

- Para debug, use `docker-compose logs -f nanobot`
- Configure recursos (CPU/Memória) baseado no uso esperado
- Use volumes para persistir dados entre atualizações
- Considere configurar health checks para auto-restart

---

**Pronto!** Seu nanobot agora está rodando no Dokploy. 🎉
