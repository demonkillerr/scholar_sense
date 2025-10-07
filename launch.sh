#!/bin/bash
set -euo pipefail

# Define cleanup function
cleanup() {
    echo "Terminating services..."
    
    # Find and terminate processes using ports 5000-5010
    echo "Checking ports 5000-5010..."
    for port in $(seq 5000 5010); do
        pid=$(sudo ss -tulnp | grep ":$port" | awk '{print $7}' | grep -o 'pid=[0-9]*' | sed 's/pid=//' | sort -u)
        if [ -n "$pid" ]; then
            echo "Terminating process on port $port: $pid"
            sudo kill -9 $pid 2>/dev/null || true
        fi
    done
    
    # Find and terminate processes using ports 3000-3010
    echo "Checking ports 3000-3010..."
    for port in $(seq 3000 3010); do
        pid=$(sudo ss -tulnp | grep ":$port" | awk '{print $7}' | grep -o 'pid=[0-9]*' | sed 's/pid=//' | sort -u)
        if [ -n "$pid" ]; then
            echo "Terminating process on port $port: $pid"
            sudo kill -9 $pid 2>/dev/null || true
        fi
    done
    
    echo "Cleanup completed."
    exit 0
}

# Register SIGINT signal handler
trap cleanup SIGINT

# Check for conda environment - without relying on SUDO_USER
echo "Checking conda environment..."
if ! command -v conda &> /dev/null; then
    echo "ERROR: conda command not found. Please make sure conda is installed and in your PATH."
    exit 1
fi

if ! conda env list | grep -q "sentiment"; then
    echo "ERROR: 'sentiment' conda environment does not exist!"
    echo "Please create the conda environment first with: conda env create -f environment.yml"
    exit 1
else
    echo "Found 'sentiment' environment, continuing..."
fi

# Start backend service in background
(
    cd apps/backend
    ./start_conda.sh
) &

# Start frontend service in background
(
    cd apps/frontend
    npm run dev
) &

echo "----- All services started ----"
echo "Press Ctrl+C to terminate all services"

# Keep the script running
wait
