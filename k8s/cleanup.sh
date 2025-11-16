#!/bin/bash
# Clean up ScholarSense Kubernetes deployment

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

echo -e "${RED}========================================${NC}"
echo -e "${RED}ScholarSense Cleanup${NC}"
echo -e "${RED}========================================${NC}"

read -p "This will delete all ScholarSense resources. Continue? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    exit 1
fi

echo -e "${GREEN}Deleting namespace and all resources...${NC}"
kubectl delete namespace scholarsense

echo -e "${GREEN}Cleanup complete!${NC}"
