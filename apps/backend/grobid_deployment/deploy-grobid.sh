#!/bin/bash

# Script for deploying GROBID
# Author: Claude
# Date: 2024

# Color definitions
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No color

# Print colored messages
print_message() {
  echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
  echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
  echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is installed
check_docker() {
  if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first: https://docs.docker.com/get-docker/"
    exit 1
  fi
  print_message "Docker is installed."
}

# Check if GPU support is available
check_gpu() {
  if command -v nvidia-smi &> /dev/null; then
    print_message "NVIDIA GPU detected."
    HAS_GPU=true
  else
    print_warning "No NVIDIA GPU detected or NVIDIA drivers not installed. Will use CPU mode."
    HAS_GPU=false
  fi
}

# Deploy GROBID
deploy_grobid() {
  local version="0.8.1"
  local port="8070"
  local host_port="8070"
  local image_type="light"
  local detached=false

  # Parse command line arguments
  while [[ $# -gt 0 ]]; do
    case $1 in
      --version)
        version="$2"
        shift 2
        ;;
      --port)
        host_port="$2"
        shift 2
        ;;
      --type)
        image_type="$2"
        shift 2
        ;;
      --detached|-d)
        detached=true
        shift
        ;;
      *)
        print_error "Unknown parameter: $1"
        exit 1
        ;;
    esac
  done

  # Choose Docker image based on image type
  if [[ "$image_type" == "full" ]]; then
    IMAGE="grobid/grobid:${version}"
    print_message "Using full version image (includes deep learning models)"
  elif [[ "$image_type" == "light" ]]; then
    IMAGE="lfoppiano/grobid:${version}"
    print_message "Using lightweight image (CRF models only)"
  else
    print_error "Invalid image type: ${image_type}. Please use 'full' or 'light'"
    exit 1
  fi

  # Pull Docker image
  print_message "Pulling ${IMAGE} image..."
  docker pull ${IMAGE}

  # Build Docker run command
  DOCKER_CMD="docker run --rm --init --ulimit core=0"
  
  # Add GPU support (if available)
  if [[ "$HAS_GPU" == true && "$image_type" == "full" ]]; then
    DOCKER_CMD="${DOCKER_CMD} --gpus all"
  fi

  # Add port mapping
  DOCKER_CMD="${DOCKER_CMD} -p ${host_port}:${port}"
  
  # Add health check port
  health_port=$((host_port + 1))
  DOCKER_CMD="${DOCKER_CMD} -p ${health_port}:8071"
  
  # Add background running parameter
  if [[ "$detached" == true ]]; then
    DOCKER_CMD="${DOCKER_CMD} -d"
  fi
  
  # Add image name
  DOCKER_CMD="${DOCKER_CMD} ${IMAGE}"

  # Run Docker container
  print_message "Starting GROBID container..."
  print_message "Executing command: ${DOCKER_CMD}"
  eval ${DOCKER_CMD}

  # If successfully started, display access information
  if [[ $? -eq 0 && "$detached" == true ]]; then
    print_message "GROBID has been successfully started in the background!"
    print_message "Access GROBID: http://localhost:${host_port}"
    print_message "Health check: http://localhost:${health_port}"
  elif [[ $? -eq 0 ]]; then
    print_message "GROBID has been successfully started!"
    print_message "Access in browser: http://localhost:${host_port}"
  else
    print_error "Failed to start GROBID. Please check the error messages."
  fi
}

# Main function
main() {
  print_message "Starting GROBID deployment..."
  check_docker
  check_gpu
  deploy_grobid "$@"
}

# Show help information
show_help() {
  echo "Usage: $0 [options]"
  echo ""
  echo "Options:"
  echo "  --version VERSION    Specify GROBID version (default: 0.8.1)"
  echo "  --port PORT          Specify host port (default: 8070)"
  echo "  --type TYPE          Specify image type: 'full' or 'light' (default: full)"
  echo "  --detached, -d       Run container in background"
  echo ""
  echo "Examples:"
  echo "  $0 --type light --port 8070 -d    Run lightweight GROBID in background, mapped to port 8070"
}

# If no arguments or help argument, show help information
if [[ $# -eq 0 || "$1" == "--help" || "$1" == "-h" ]]; then
  show_help
  exit 0
fi

# Run main function
main "$@" 