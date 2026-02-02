# Nanobot Docker + Dokploy

Deploy do **nanobot** com Docker otimizado para **Dokploy**.

## 🚀 Quick Start (Dokploy)

```bash
# 1. Clone este repositório
git clone https://github.com/pve/nanobot-ai.git
cd nanobot-ai
git checkout claude/add-dockerfile-uv-1i3Kt

# 2. Configure as variáveis de ambiente
cp .env.example .env
nano .env

# 3. Push para GitHub
git add .
git commit -m "Configure for Dokploy"
git push origin claude/add-dockerfile-uv-1i3Kt

# 4. Deploy no Dokploy
# - Import o repositório no Dokploy
# - Configure para usar docker-compose.yml
# - Deploy!
```

## 📚 Documentação Completa

Veja [DOKPLOY.md](./DOKPLOY.md) para instruções detalhadas de deploy.

## 🔧 Arquivos Incluídos

- **`docker-compose.yml`** - Configuração otimizada para Dokploy
- **`.env.example`** - Template de variáveis de ambiente
- **`Dockerfile`** - Imagem Docker com Python 3.12 + Node.js 20
- **`DOKPLOY.md`** - Guia completo de deploy

## 🐳 Local Testing

Teste localmente antes do deploy:

```bash
# Build
docker build -t nanobot .

# Run
docker run --rm nanobot onboard

# Gateway
docker run -v ~/.nanobot:/root/.nanobot -p 18790:18790 nanobot gateway
```

## 🎯 Funcionalidades

- ✅ Python 3.12 com uv (gerenciador rápido de pacotes)
- ✅ Node.js 20 para bridge do WhatsApp
- ✅ Gateway na porta 18790
- ✅ Persistência de configuração via volume
- ✅ Health check configurado
- ✅ Logs rotacionados
- ✅ Limits de recursos configuráveis

## 📱 Canais Suportados

- **Telegram** - Fácil configuração via BotFather
- **WhatsApp** - Requer scan de QR code

Veja [DOKPLOY.md](./DOKPLOY.md) para instruções de configuração.

## 🔄 Atualizações

Este repositório segue o branch `claude/add-dockerfile-uv-1i3Kt` do fork do pve, que contém o PR #18 do nanobot com suporte Docker.

## 🤝 Contribuindo

Contribuições são bem-vindas! Por favor:
1. Fork o repositório
2. Crie um branch para sua feature
3. Commit suas mudanças
4. Push para o branch
5. Abra um Pull Request

## 📄 Licença

MIT - Veja [LICENSE](./LICENSE) para detalhes.

## 🙋 Suporte

- **Issues**: https://github.com/HKUDS/nanobot/issues
- **PR Docker**: https://github.com/HKUDS/nanobot/pull/18

---

**Made with ❤️ for the nanobot community**
