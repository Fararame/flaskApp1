#!/bin/sh
# build_docker.sh - Build or pull Docker image for cs212exam1 / docker.flaskapp0

# Load environment variables from .env.dev if it exists
[ -f "$PWD/.env.dev" ] && . "$PWD/.env.dev"

app="cs212exam1"
image_name="docker.flaskapp0"
registry_server="10.4.29.209:30500"
tag="latest"

# Environment variable controls
FORCE_BUILD="${FORCE_BUILD:-false}"
PULL_REGISTRY="${PULL_REGISTRY:-true}"

echo "========================================"
echo "Building/Running ${app}"
echo "Registry: ${registry_server}/${image_name}:${tag}"
echo "FORCE_BUILD=${FORCE_BUILD}"
echo "PULL_REGISTRY=${PULL_REGISTRY}"
echo "========================================"

# Function to check if registry is accessible
check_registry() {
    echo "Checking registry availability at ${registry_server}..."

    # Basic ping check (host reachable)
    if ! ping -c 1 -W 2 "${registry_server%:*}" >/dev/null 2>&1; then
        echo "Registry host ${registry_server%:*} is not reachable via ping"
        return 1
    fi

    # Check Docker registry v2 API (_catalog endpoint)
    if ! curl -s --connect-timeout 5 "http://${registry_server}/v2/_catalog" >/dev/null 2>&1; then
        echo "Registry API at ${registry_server} is not responding"
        return 1
    fi

    echo "Registry ${registry_server} is accessible"
    return 0
}

# Main logic
if [ "$FORCE_BUILD" = "true" ]; then
    echo "FORCE_BUILD=true → skipping pull and building locally"
    docker build -t "${app}" .
elif [ "$PULL_REGISTRY" = "false" ]; then
    echo "PULL_REGISTRY=false → skipping pull and building locally"
    docker build -t "${app}" .
elif check_registry; then
    echo "Registry is available, attempting to pull image..."
    echo "Pulling ${registry_server}/${image_name}:${tag} ..."

    if docker pull "${registry_server}/${image_name}:${tag}"; then
        echo "Pull successful → tagging locally as ${app}"
        docker tag "${registry_server}/${image_name}:${tag}" "${app}"
    else
        echo "Pull failed (possibly insecure registry, network, or proxy issue)"
        echo "Falling back to local build..."
        docker build -t "${app}" .
    fi
else
    echo "Registry check failed → falling back to local build"
    docker build -t "${app}" .
fi

# Clean up any old container with same name
echo "Removing any existing container named ${app}..."
docker rm -f "${app}" 2>/dev/null || true

# Run the container
echo "Starting container ${app}..."
docker run -d \
  --name "${app}" \
  -p 56733:8000 \
  -e FLASK_DEBUG="${FLASK_DEBUG:-0}" \
  -v "$PWD":/flask_app \
  "${app}"

# Verify it's running
sleep 2  # give it a moment to start
if docker ps --filter "name=${app}" --filter "status=running" --quiet | grep -q .; then
    echo "Success: Container ${app} is running"
    echo "Access the app at: http://localhost:56733"
    echo ""
    echo "Useful commands:"
    echo "  docker logs ${app}          # view logs"
    echo "  docker stop ${app}          # stop"
    echo "  docker rm -f ${app}         # force remove"
else
    echo "ERROR: Container ${app} failed to start!"
    echo "Check logs:"
    docker logs "${app}"
    exit 1
fi
