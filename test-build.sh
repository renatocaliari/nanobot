#!/usr/bin/env bash
set -euo pipefail

echo "=== Nanobot Docker Build Test ==="
echo ""
echo "Este script testa se o Dockerfile está configurado corretamente."
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker não está instalado."
    echo ""
    echo "Por favor, instale o Docker:"
    echo "  - macOS: https://docs.docker.com/desktop/install/mac-install/"
    echo "  - Linux: curl -fsSL https://get.docker.com | sh"
    echo ""
    exit 1
fi

echo "✅ Docker está instalado: $(docker --version)"
echo ""

# Build the image
echo "=== Building Docker image ==="
docker build -t nanobot-test .

echo ""
echo "=== Running 'nanobot status' ==="
docker run --rm nanobot-test status

echo ""
echo "=== Test completed successfully! ==="
echo ""
echo "A imagem Docker está pronta para deploy no Dokploy."
echo ""
