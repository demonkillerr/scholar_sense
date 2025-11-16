# ScholarSense Kubernetes Deployment

## Prerequisites

- Kubernetes cluster (minikube, kind, k3s, or cloud provider)
- kubectl configured
- Docker images built locally

## Quick Start

### 1. Build Docker Images

```bash
cd /home/dk/code/projects/scholar_sense

# Build backend
docker build -t scholar_sense-backend:latest ./apps/backend

# Build frontend
docker build -t scholar_sense-frontend:latest ./apps/frontend
```

### 2. Configure Secrets

Edit `k8s/backend-secret.yaml` and add your Gemini API key:

```yaml
stringData:
  GEMINI_API_KEY: "your_actual_api_key_here"
```

### 3. Deploy to Kubernetes

```bash
# Create namespace
kubectl apply -f k8s/namespace.yaml

# Create secrets and config
kubectl apply -f k8s/backend-secret.yaml
kubectl apply -f k8s/backend-configmap.yaml

# Create persistent volumes
kubectl apply -f k8s/backend-pvc.yaml

# Deploy services
kubectl apply -f k8s/grobid-deployment.yaml
kubectl apply -f k8s/backend-deployment.yaml
kubectl apply -f k8s/frontend-deployment.yaml

# Optional: Apply ingress (requires nginx-ingress-controller)
kubectl apply -f k8s/ingress.yaml
```

### 4. Access the Application

#### Option 1: NodePort (Direct Access)

```bash
# Frontend is exposed on NodePort 30000
# Access at: http://localhost:30000

# For minikube:
minikube service frontend -n scholarsense
```

#### Option 2: Port Forward

```bash
# Frontend
kubectl port-forward -n scholarsense svc/frontend 3000:3000

# Backend (optional, for direct API access)
kubectl port-forward -n scholarsense svc/backend 5000:5000

# GROBID (optional, for testing)
kubectl port-forward -n scholarsense svc/grobid 8070:8070
```

Then access:
- Frontend: http://localhost:3000
- Backend API: http://localhost:5000/status
- GROBID: http://localhost:8070/api/isalive

#### Option 3: Ingress (with nginx-ingress-controller)

```bash
# Install nginx ingress controller first
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.1/deploy/static/provider/cloud/deploy.yaml

# Add to /etc/hosts:
# 127.0.0.1 scholarsense.local

# Access at: http://scholarsense.local
```

## Management Commands

### Check Status

```bash
# All resources
kubectl get all -n scholarsense

# Pods
kubectl get pods -n scholarsense

# Services
kubectl get svc -n scholarsense

# Logs
kubectl logs -n scholarsense -l app=backend --tail=50
kubectl logs -n scholarsense -l app=frontend --tail=50
kubectl logs -n scholarsense -l app=grobid --tail=50
```

### Scaling

```bash
# Scale backend replicas
kubectl scale deployment/backend -n scholarsense --replicas=2

# Scale frontend replicas
kubectl scale deployment/frontend -n scholarsense --replicas=3
```

### Update Deployment

```bash
# After rebuilding Docker images
kubectl rollout restart deployment/backend -n scholarsense
kubectl rollout restart deployment/frontend -n scholarsense

# Check rollout status
kubectl rollout status deployment/backend -n scholarsense
```

### Troubleshooting

```bash
# Describe pod for details
kubectl describe pod -n scholarsense <pod-name>

# Get pod shell
kubectl exec -it -n scholarsense <pod-name> -- /bin/bash

# View events
kubectl get events -n scholarsense --sort-by='.lastTimestamp'

# Check persistent volumes
kubectl get pvc -n scholarsense
```

### Clean Up

```bash
# Delete all resources
kubectl delete namespace scholarsense

# Or delete individually
kubectl delete -f k8s/frontend-deployment.yaml
kubectl delete -f k8s/backend-deployment.yaml
kubectl delete -f k8s/grobid-deployment.yaml
kubectl delete -f k8s/backend-pvc.yaml
kubectl delete -f k8s/backend-configmap.yaml
kubectl delete -f k8s/backend-secret.yaml
kubectl delete -f k8s/namespace.yaml
```

## Using with Minikube

```bash
# Start minikube
minikube start --memory=8192 --cpus=4

# Load local images into minikube
minikube image load scholar_sense-backend:latest
minikube image load scholar_sense-frontend:latest

# Deploy
kubectl apply -f k8s/

# Access services
minikube service frontend -n scholarsense
minikube service backend -n scholarsense

# Stop
minikube stop
```

## Using with kind

```bash
# Create cluster
kind create cluster --name scholarsense

# Load images
kind load docker-image scholar_sense-backend:latest --name scholarsense
kind load docker-image scholar_sense-frontend:latest --name scholarsense

# Deploy
kubectl apply -f k8s/

# Access via port-forward
kubectl port-forward -n scholarsense svc/frontend 3000:3000
```

## Production Considerations

### 1. Use Container Registry

Instead of `imagePullPolicy: Never`, push images to a registry:

```yaml
image: your-registry.com/scholarsense/backend:v1.0.0
imagePullPolicy: Always
```

### 2. Configure Resources

Adjust resource requests/limits based on your workload:

```yaml
resources:
  requests:
    memory: "4Gi"
    cpu: "1000m"
  limits:
    memory: "8Gi"
    cpu: "2000m"
```

### 3. Add TLS

Update ingress with TLS:

```yaml
spec:
  tls:
  - hosts:
    - scholarsense.yourdomain.com
    secretName: scholarsense-tls
```

### 4. Add Monitoring

Deploy Prometheus & Grafana for monitoring:

```bash
helm install prometheus prometheus-community/kube-prometheus-stack -n monitoring
```

### 5. Enable Autoscaling

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: backend-hpa
  namespace: scholarsense
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: backend
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

## Architecture

```
┌─────────────────────────────────────────┐
│         Ingress (Optional)              │
│    scholarsense.local                   │
└──────────────┬──────────────────────────┘
               │
       ┌───────┴────────┐
       │                │
   ┌───▼────┐      ┌────▼────┐
   │Frontend│      │ Backend │
   │Service │      │ Service │
   │  :3000 │      │  :5000  │
   └───┬────┘      └────┬────┘
       │                │
   ┌───▼────┐      ┌────▼──────────┐
   │Frontend│      │    Backend    │
   │  Pod   │      │     Pod       │
   │        │      │               │
   │Next.js │      │Flask + RAG    │
   └────────┘      │+ ChromaDB     │
                   │+ BGE Model    │
                   └────┬──────────┘
                        │
                   ┌────▼────┐
                   │ GROBID  │
                   │ Service │
                   │  :8070  │
                   └────┬────┘
                        │
                   ┌────▼────┐
                   │ GROBID  │
                   │  Pod    │
                   └─────────┘
```

## Storage

- **backend-uploads**: Stores uploaded PDF files (10Gi)
- **backend-chromadb**: Stores vector database (20Gi)

Both use PersistentVolumeClaims that will be automatically provisioned by your cluster's default storage class.

## Environment Variables

### Backend

- `FLASK_ENV`: Flask environment (production/development)
- `DEBUG`: Enable debug mode (True/False)
- `GROBID_URL`: GROBID service URL (http://grobid:8070)
- `GEMINI_API_KEY`: Google Gemini API key (secret)
- `UPLOAD_FOLDER`: PDF upload directory
- `VECTOR_STORE_PATH`: ChromaDB storage path
- `EMBEDDING_MODEL`: Sentence transformer model name

### Frontend

- `NEXT_PUBLIC_API_URL`: Backend API URL (http://backend:5000)
- `NODE_ENV`: Node environment (production/development)

## Deployment Paths

### Local Development (Minikube)
Use for testing and development on your local machine.
See sections above for Minikube setup.

### Production (GCP GKE)
For production deployment with autoscaling, load balancing, and SSL.
See **[GCP_DEPLOYMENT.md](GCP_DEPLOYMENT.md)** for complete guide.

**TL;DR for GCP**:
1. Run `./k8s/setup-gcp.sh` to configure for GCP
2. Create GKE cluster
3. Push images: `./push-to-gcr.sh`
4. Deploy: `kubectl apply -k k8s/overlays/gcp`

**The same Kubernetes manifests work on both!** 🎉

## Next Steps

1. Deploy to your cluster (Minikube or GKE)
2. Test with sample papers
3. Set up monitoring (Prometheus/Grafana)
4. Configure backups for PVCs
5. For GCP: Set up SSL with cert-manager
6. Add authentication (future enhancement)
