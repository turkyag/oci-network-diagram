#!/usr/bin/env bash
set -euo pipefail

echo "=== OCI Network Explorer — Upgrade ==="
echo ""

# Pull latest code
echo "Pulling latest changes..."
git pull origin main

# Rebuild containers with new code
echo "Rebuilding containers..."
docker compose build

# Restart with new code (DB migrations auto-apply on backend start)
echo "Restarting services..."
docker compose up -d

echo ""
echo "=== Upgrade complete ==="
echo "Frontend: http://localhost:3000"
echo ""
echo "If you need to re-sync OCI data:"
echo "  docker compose run --rm oci-sync sync.py --config-file /oci/config"
