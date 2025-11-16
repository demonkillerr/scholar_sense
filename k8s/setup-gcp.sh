#!/bin/bash
# ScholarSense GCP Deployment Helper

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}ScholarSense GCP Deployment Setup${NC}"
echo -e "${BLUE}========================================${NC}"

# Get project ID
read -p "Enter your GCP Project ID: " PROJECT_ID
if [ -z "$PROJECT_ID" ]; then
    echo "Project ID cannot be empty"
    exit 1
fi

# Get region/zone
read -p "Enter GCP zone (default: us-central1-a): " ZONE
ZONE=${ZONE:-us-central1-a}

echo ""
echo -e "${GREEN}Configuration:${NC}"
echo "  Project ID: $PROJECT_ID"
echo "  Zone: $ZONE"
echo ""

# Update image references
echo -e "${YELLOW}Updating image references in manifests...${NC}"

mkdir -p k8s/overlays/gcp

cat > k8s/overlays/gcp/kustomization.yaml <<EOF
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

namespace: scholarsense

bases:
  - ../../

images:
  - name: scholar_sense-backend
    newName: gcr.io/$PROJECT_ID/backend
    newTag: latest
  - name: scholar_sense-frontend
    newName: gcr.io/$PROJECT_ID/frontend
    newTag: latest

patchesStrategicMerge:
  - frontend-service-patch.yaml
  - backend-deployment-patch.yaml
  - frontend-deployment-patch.yaml
EOF

cat > k8s/overlays/gcp/frontend-service-patch.yaml <<EOF
apiVersion: v1
kind: Service
metadata:
  name: frontend
spec:
  type: LoadBalancer
  ports:
  - port: 80
    targetPort: 3000
EOF

cat > k8s/overlays/gcp/backend-deployment-patch.yaml <<EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend
spec:
  template:
    spec:
      containers:
      - name: backend
        imagePullPolicy: Always
EOF

cat > k8s/overlays/gcp/frontend-deployment-patch.yaml <<EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: frontend
spec:
  template:
    spec:
      containers:
      - name: frontend
        imagePullPolicy: Always
EOF

echo -e "${GREEN}✓ GCP overlay created${NC}"
echo ""

# Create push script
cat > push-to-gcr.sh <<EOF
#!/bin/bash
# Push Docker images to GCR

set -e

echo "Tagging images..."
docker tag scholar_sense-backend:latest gcr.io/$PROJECT_ID/backend:latest
docker tag scholar_sense-frontend:latest gcr.io/$PROJECT_ID/frontend:latest

echo "Pushing to GCR..."
docker push gcr.io/$PROJECT_ID/backend:latest
docker push gcr.io/$PROJECT_ID/frontend:latest

echo "✓ Images pushed to GCR"
EOF

chmod +x push-to-gcr.sh

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Setup Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Next steps:"
echo ""
echo "1. Configure GCP:"
echo "   gcloud config set project $PROJECT_ID"
echo "   gcloud auth configure-docker"
echo ""
echo "2. Create GKE cluster:"
echo "   gcloud container clusters create scholarsense-cluster \\"
echo "     --zone $ZONE \\"
echo "     --num-nodes 3 \\"
echo "     --machine-type n1-standard-4"
echo ""
echo "3. Push images:"
echo "   ./push-to-gcr.sh"
echo ""
echo "4. Deploy:"
echo "   kubectl apply -k k8s/overlays/gcp"
echo ""
echo "5. Get LoadBalancer IP:"
echo "   kubectl get svc frontend -n scholarsense"
echo ""
