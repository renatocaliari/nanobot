# Deployment Strategy: Mem0 + Nanobot

## 🎯 Pergunta: Preciso de outro projeto Dokploy ou posso rodar junto?

## ✅ Resposta: RODE JUNTO! (Recomendado)

---

## Opção 1: Mesmo Projeto Dokploy (RECOMENDADO) ⭐

### Arquitetura

```
Dokploy Project: nanobot
├── Container 1: nanobot (seu app)
├── Container 2: mem0 (servidor de memória)
└── Container 3: postgres (banco de dados)
```

### Vantagens

✅ **Simples** - Um só projeto para gerenciar
✅ **Custo menor** - Compartilha recursos
✅ **Performance** - Comunicação local (rede interna)
✅ **Manutenção** - Menos projetos para gerenciar

### docker-compose.yml Modificado

```yaml
version: '3.8'

services:
  # Mem0 + Database
  mem0:
    image: mem0ai/mem0:latest
    ports:
      - "8000:8000"
    environment:
      - POSTGRES_URI=postgresql://mem0:postgres@postgres:5432/mem0db
    depends_on:
      - postgres
    restart: unless-stopped

  postgres:
    image: postgres:15
    environment:
      - POSTGRES_USER=mem0user
      - POSTGRES_PASSWORD=mem0pass
      - POSTGRES_DB=mem0db
    volumes:
      - mem0-data:/var/lib/postgresql/data
    restart: unless-stopped

  # Nanobot
  nanobot:
    build: .
    ports:
      - "18790:18790"
    environment:
      # LLM
      - NANOBOT_PROVIDERS__ZAI__API_KEY=${ZAI_API_KEY}
      
      # Mem0 (replaces Supermemory)
      - MEM0_URL=http://mem0:8000
      - MEM0_ENABLED=true
      
      # Telegram
      - NANOBOT_CHANNELS__TELEGRAM__ENABLED=true
      - NANOBOT_CHANNELS__TELEGRAM__TOKEN=${TELEGRAM_TOKEN}
    depends_on:
      - mem0
    volumes:
      - ./bots.json:/app/config/bots.json:ro
      - ./workspace:/root/.nanobot/workspace
    restart: unless-stopped

volumes:
  mem0-data:
```

### Configuração Dokploy

**Passo 1**: Criar projeto no Dokploy
- Nome: `nanobot`
- Repositório: `https://github.com/renatocaliari/nanobot.git`
- Branch: `claude/add-dockerfile-uv-1i3Kt`
- Docker Compose: Usar `docker-compose.mem0.yml`

**Passo 2**: Variáveis de ambiente
```
ZAI_API_KEY=z-xxxxxxxxxxxxx
TELEGRAM_TOKEN=seu_bot_token
MEM0_URL=http://mem0:8000
```

**Passo 3**: Deploy
- Build e deploy normalmente
- Dokploy iniciará 3 containers: mem0, postgres, nanobot

---

## Opção 2: Projetos Separados

### Quando usar?

**Use separados se:**
- ⚠️ Quer escalar Mem0 independentemente
- ⚠️ Múltiplos apps usam Mem0
- ⚠️ Quer isolar recursos completamente
- ⚠️ Time diferente gerencia Mem0

### Arquitetura

```
Dokploy Project 1: mem0
└── mem0 + postgres + qdrant

Dokploy Project 2: nanobot
└── nanobot (conecta em mem0 do projeto 1)
```

### Desvantagens

❌ **Mais complexo** - 2 projetos para gerenciar
❌ **Comunicação externa** - Mais latência
❌ **Custo maior** - 2 projetos separados
❌ **Configuração extra** - CORS, URLs públicas

---

## 💡 Recomendação: Use Opção 1 (Mesmo Projeto)

**Por que?**

1. **Simplicidade**
   - Um projeto só
   - Deploy em um clique
   - Menos coisas pra dar manutenção

2. **Performance**
   - Comunicação via rede interna Docker
   - Latência < 1ms vs 10-50ms
   - Sem necessidade de expor portas publicamente

3. **Custo**
   - Compartilha recursos
   - Apenas 1 projeto no Dokploy (dependendo do plano)
   - Menos overhead

4. **Multi-bot facilitado**
   - Mem0 já suporta multi-tenancy por `user_id`
   - Cada bot tem suas memórias separadas automaticamente
   - Sem necessidade de múltiplas instâncias Mem0

---

## 📊 Comparativo

| Aspecto               | Mesmo Projeto | Projetos Separados |
| --------------------- | -------------- | ------------------ |
| **Complexidade**        | ✅ Baixa      | ❌ Alta            |
| **Latência**           | ✅ <1ms        | ❌ 10-50ms        |
| **Custo**              | ✅ Menor       | ❌ Maior           |
| **Manutenção**         | ✅ 1 projeto    | ❌ 2+ projetos      |
| **Escalabilidade**     | ⚠️ Média      | ✅ Alta            |
| **Isolamento completo**| ❌ Parcial     | ✅ Total           |

---

## 🚀 Implementação

### 1. Criar docker-compose.mem0.yml

Já criado acima! ✅

### 2. Atualizar DOKPLOY.md

Adicionar seção sobre Mem0 deployment.

### 3. Testar localmente

```bash
# Testar deploy local
docker-compose -f docker-compose.mem0.yml up -d

# Ver se tudo subiu
docker-compose ps

# Ver logs
docker logs nanobot
docker logs mem0
```

### 4. Deploy no Dokploy

- Usar `docker-compose.mem0.yml` como base
- Configurar variáveis de ambiente
- Deploy!

---

## ✅ Conclusão

**Rode Mem0 junto com nanobot no MESMO projeto Dokploy!**

**Só não use projetos separados se:**
- Você precisar escalar Mem0 para dezenas de apps
- Time diferente gerenciando infra
- Quer isolamento completo de recursos

**Para multi-bot pessoal? Mesmo projeto é perfeito!** ✅
