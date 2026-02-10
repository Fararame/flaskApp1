#!/bin/bash

# Configuration
REGISTRY_IP="10.4.29.209"
REGISTRY_PORT="30500"
REGISTRY_COMPOSE_FILE="docker-compose.challenge.yml"
LOCAL_COMPOSE_FILE="docker-compose.yml"
ENV_FILE=".env.dev"

# Database Configuration
POSTGRES_USER="hello_flask"
POSTGRES_PASSWORD="hello_flask"
POSTGRES_DB="hello_flask_dev"
DATABASE_URL="postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@db:5432/${POSTGRES_DB}"

# Export variables for docker compose substitution
export REGISTRY_IP
export REGISTRY_PORT
export POSTGRES_USER
export POSTGRES_PASSWORD
export POSTGRES_DB
export DATABASE_URL

echo "=========================================="
echo "Starting Lab Challenge Setup"
echo "=========================================="
echo "Registry: ${REGISTRY_IP}:${REGISTRY_PORT}"
echo "Database: ${POSTGRES_DB} (User: ${POSTGRES_USER})"

echo "[1/2] Attempting to pull and start using exam registry (${REGISTRY_IP}:${REGISTRY_PORT})..."

# Try to pull images first to verify connectivity/availability
if docker compose --env-file "$ENV_FILE" -f "$REGISTRY_COMPOSE_FILE" pull; then
    echo "Images pulled successfully."
    
    echo "Starting services..."
    if docker compose --env-file "$ENV_FILE" -f "$REGISTRY_COMPOSE_FILE" --compatibility up -d; then
        echo "=========================================="
        echo "SUCCESS: Lab started using registry images."
        echo "=========================================="
        exit 0
    else
        echo "WARNING: Failed to start services despite successful pull."
    fi
else
    echo "WARNING: Failed to pull images from registry. (Registry might be unreachable)"
fi

echo ""
echo "[2/2] Failing back to local build..."
echo "Building and starting using local source ($LOCAL_COMPOSE_FILE)..."

# Build (if necessary) and up using the local compose file
if docker compose --env-file "$ENV_FILE" -f "$LOCAL_COMPOSE_FILE" --compatibility up -d --build; then
    echo "=========================================="
    echo "SUCCESS: Lab started using local build (Fallback)."
    echo "=========================================="
    exit 0
else
    echo "=========================================="
    echo "ERROR: Failed to start lab using local build."
    echo "Please check the error messages above."
    echo "=========================================="
    exit 1
fi
