#!/bin/bash
# ScholarSense Kubernetes Deployment Script

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}ScholarSense Kubernetes Deployment${NC}"
echo -e "${GREEN}========================================${NC}"

# Check if kubectl is installed
if ! command -v kubectl &> /dev/null; then
    echo -e "${RED}kubectl is not installed. Please install it first.${NC}"
    exit 1
fi

# Check if API key is set
if grep -q "YOUR_GEMINI_API_KEY_HERE" k8s/backend-secret.yaml; then
    echo -e "${YELLOW}⚠️  Warning: Gemini API key not set in k8s/backend-secret.yaml${NC}"
    echo -e "${YELLOW}Please edit the file and add your API key before proceeding.${NC}"
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo -e "${GREEN}1. Creating namespace...${NC}"
kubectl apply -f k8s/namespace.yaml

echo -e "${GREEN}2. Creating secrets and config...${NC}"
kubectl apply -f k8s/backend-secret.yaml
kubectl apply -f k8s/backend-configmap.yaml

echo -e "${GREEN}3. Creating persistent volumes...${NC}"
kubectl apply -f k8s/backend-pvc.yaml

echo -e "${GREEN}4. Deploying GROBID...${NC}"
kubectl apply -f k8s/grobid-deployment.yaml

echo -e "${GREEN}5. Deploying Backend...${NC}"
kubectl apply -f k8s/backend-deployment.yaml

echo -e "${GREEN}6. Deploying Frontend...${NC}"
kubectl apply -f k8s/frontend-deployment.yaml

echo -e "${GREEN}7. Checking deployment status...${NC}"
kubectl get all -n scholarsense

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Deployment initiated!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "To check status:"
echo "  kubectl get pods -n scholarsense"
echo ""
echo "To view logs:"
echo "  kubectl logs -n scholarsense -l app=backend --tail=50"
echo "  kubectl logs -n scholarsense -l app=frontend --tail=50"
echo ""
echo "To access the application:"
echo "  kubectl port-forward -n scholarsense svc/frontend 3000:3000"
echo "  Then open: http://localhost:3000"
echo ""
echo -e "${YELLOW}Note: It may take a few minutes for all pods to be ready.${NC}"
