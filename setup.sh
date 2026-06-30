#!/bin/bash

set -e

echo "=== DevOps Final Project Setup ==="

if ! command -v docker &> /dev/null; then
    echo "ERROR: Docker is not installed. Install Docker first."
    exit 1
fi

if ! docker compose version &> /dev/null; then
    echo "ERROR: Docker Compose is not available. Install Docker Desktop or the compose plugin."
    exit 1
fi

if [ ! -f .env ]; then
    echo "Creating .env from .env.example..."
    cp .env.example .env
fi

echo "Starting all services"
docker compose up -d --build

echo "Waiting for services to start"
sleep 5

echo "Run health checks"

if curl -sf http://localhost:5000/health > /dev/null; then
    echo "Flask app is UP"
else
    echo "WARNING: Flask app not responding"
fi

if curl -sf http://localhost:9090/-/ready > /dev/null; then
    echo "Prometheus is UP"
else
    echo "WARNING: Prometheus not responding"
fi

if curl -sf http://localhost:3000 > /dev/null; then
    echo "Grafana is UP"
else
    echo "WARNING: Grafana not responding"
fi

echo ""
echo "=== Setup complete ==="
echo "Flask app:  http://localhost:5000"
echo "Prometheus: http://localhost:9090"
echo "Grafana:    http://localhost:3000 (admin/admin)"
echo "Loki:       http://localhost:3100"