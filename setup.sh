#!/usr/bin/env bash
set -euo pipefail

echo "=== OCI Network Explorer Setup ==="
echo ""

# Check Docker
command -v docker >/dev/null 2>&1 || { echo "Error: Docker is required"; exit 1; }
command -v docker compose >/dev/null 2>&1 || { echo "Error: Docker Compose is required"; exit 1; }

# Create .env if missing
if [ ! -f .env ]; then
    cp .env.example .env
    echo "Created .env from .env.example"
fi

# Check OCI config
if [ ! -f oci-config ]; then
    echo ""
    echo "OCI config not found. Create it:"
    echo "  cp oci-config.example oci-config"
    echo "  # Edit oci-config with your OCI credentials"
    echo "  # Place your API key as oci-key.pem"
    exit 1
fi

if [ ! -f oci-key.pem ]; then
    echo ""
    echo "OCI API key not found. Place your .pem key as oci-key.pem"
    exit 1
fi

echo "Building containers..."
docker compose build

echo "Starting services..."
docker compose up -d

echo "Waiting for backend..."
for i in $(seq 1 30); do
    curl -sf http://localhost:8000/health > /dev/null 2>&1 && break
    sleep 2
done

echo ""
echo "=== Ready ==="
echo "Frontend: http://localhost:3000"
echo "Backend:  http://localhost:8000"
echo ""
echo "To sync OCI data:"
echo "  docker compose run --rm oci-sync sync.py --config-file /oci/config"
