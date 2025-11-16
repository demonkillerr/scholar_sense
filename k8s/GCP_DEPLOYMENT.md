# Deploying ScholarSense to Google Cloud Platform (GKE)

## Prerequisites

- Google Cloud account with billing enabled
- `gcloud` CLI installed ([Install Guide](https://cloud.google.com/sdk/docs/install))
- Docker images pushed to Google Container Registry (GCR) or Artifact Registry

## Step-by-Step Migration from Minikube to GKE

### 1. Set Up GCP Project

```bash
# Login to GCP
gcloud auth login

# Create a new project (or use existing)
export PROJECT_ID="scholarsense-prod"
gcloud projects create $PROJECT_ID
gcloud config set project $PROJECT_ID

# Enable required APIs
gcloud services enable container.googleapis.com
gcloud services enable containerregistry.googleapis.com
gcloud services enable compute.googleapis.com
```

### 2. Create GKE Cluster

```bash
# Create a GKE cluster (adjust specs based on your needs)
gcloud container clusters create scholarsense-cluster \
    --zone us-central1-a \
    --num-nodes 3 \
    --machine-type n1-standard-4 \
    --disk-size 100 \
    --enable-autoscaling \
    --min-nodes 2 \
    --max-nodes 5 \
    --enable-autorepair \
    --enable-autoupgrade

# Get credentials
gcloud container clusters get-credentials scholarsense-cluster --zone us-central1-a

# Verify connection
kubectl get nodes
```

**Cost Estimate**: ~$200-300/month for 3 n1-standard-4 nodes

**Budget-Friendly Option**:
```bash
# Smaller cluster for testing
gcloud container clusters create scholarsense-cluster \
    --zone us-central1-a \
    --num-nodes 2 \
    --machine-type e2-medium \
    --disk-size 50 \
    --preemptible
```

### 3. Push Docker Images to GCR

```bash
# Configure Docker for GCR
gcloud auth configure-docker

# Tag images for GCR
docker tag scholar_sense-backend:latest gcr.io/$PROJECT_ID/backend:latest
docker tag scholar_sense-frontend:latest gcr.io/$PROJECT_ID/frontend:latest

# Push to GCR
docker push gcr.io/$PROJECT_ID/backend:latest
docker push gcr.io/$PROJECT_ID/frontend:latest
```

### 4. Update Kubernetes Manifests for GKE

Create GCP-specific overlays:

```bash
mkdir -p k8s/overlays/gcp
```

**k8s/overlays/gcp/backend-deployment-patch.yaml**:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend
  namespace: scholarsense
spec:
  template:
    spec:
      containers:
      - name: backend
        image: gcr.io/PROJECT_ID/backend:latest  # Replace PROJECT_ID
        imagePullPolicy: Always  # Changed from Never
```

**k8s/overlays/gcp/frontend-deployment-patch.yaml**:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: frontend
  namespace: scholarsense
spec:
  template:
    spec:
      containers:
      - name: frontend
        image: gcr.io/PROJECT_ID/frontend:latest  # Replace PROJECT_ID
        imagePullPolicy: Always  # Changed from Never
```

**k8s/overlays/gcp/frontend-service.yaml**:
```yaml
apiVersion: v1
kind: Service
metadata:
  name: frontend
  namespace: scholarsense
spec:
  type: LoadBalancer  # Changed from NodePort for GCP
  ports:
  - port: 80
    targetPort: 3000
    protocol: TCP
    name: http
  selector:
    app: frontend
```

**k8s/overlays/gcp/storage-class.yaml**:
```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: fast-ssd
provisioner: kubernetes.io/gce-pd
parameters:
  type: pd-ssd  # Use SSD for better ChromaDB performance
  replication-type: none
allowVolumeExpansion: true
```

**k8s/overlays/gcp/backend-pvc.yaml**:
```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: backend-uploads
  namespace: scholarsense
spec:
  accessModes:
    - ReadWriteOnce
  storageClassName: fast-ssd  # Use SSD storage class
  resources:
    requests:
      storage: 50Gi  # Increased for production
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: backend-chromadb
  namespace: scholarsense
spec:
  accessModes:
    - ReadWriteOnce
  storageClassName: fast-ssd
  resources:
    requests:
      storage: 100Gi  # Increased for production
```

### 5. Deploy to GKE

```bash
# Create storage class
kubectl apply -f k8s/overlays/gcp/storage-class.yaml

# Deploy base configuration
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/backend-secret.yaml
kubectl apply -f k8s/backend-configmap.yaml

# Deploy GCP-specific PVCs
kubectl apply -f k8s/overlays/gcp/backend-pvc.yaml

# Deploy services
kubectl apply -f k8s/grobid-deployment.yaml
kubectl apply -f k8s/backend-deployment.yaml
kubectl apply -f k8s/overlays/gcp/backend-deployment-patch.yaml
kubectl apply -f k8s/frontend-deployment.yaml
kubectl apply -f k8s/overlays/gcp/frontend-deployment-patch.yaml
kubectl apply -f k8s/overlays/gcp/frontend-service.yaml
```

### 6. Set Up Ingress with HTTPS

```bash
# Install nginx-ingress-controller
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.1/deploy/static/provider/cloud/deploy.yaml

# Wait for LoadBalancer IP
kubectl get svc -n ingress-nginx
```

**k8s/overlays/gcp/ingress-https.yaml**:
```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: scholarsense-ingress
  namespace: scholarsense
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
    nginx.ingress.kubernetes.io/proxy-body-size: "50m"
spec:
  ingressClassName: nginx
  tls:
  - hosts:
    - scholarsense.yourdomain.com
    secretName: scholarsense-tls
  rules:
  - host: scholarsense.yourdomain.com
    http:
      paths:
      - path: /api
        pathType: Prefix
        backend:
          service:
            name: backend
            port:
              number: 5000
      - path: /
        pathType: Prefix
        backend:
          service:
            name: frontend
            port:
              number: 3000
```

### 7. Set Up SSL with cert-manager

```bash
# Install cert-manager
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml

# Create ClusterIssuer for Let's Encrypt
cat <<EOF | kubectl apply -f -
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: your-email@example.com
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
    - http01:
        ingress:
          class: nginx
EOF

# Apply HTTPS ingress
kubectl apply -f k8s/overlays/gcp/ingress-https.yaml
```

### 8. Configure DNS

```bash
# Get the LoadBalancer IP
kubectl get ingress -n scholarsense

# Add an A record in your DNS provider:
# scholarsense.yourdomain.com -> [EXTERNAL-IP]
```

### 9. Set Up Cloud SQL (Optional, for better ChromaDB)

Instead of local ChromaDB, you can use Cloud SQL PostgreSQL with pgvector:

```bash
# Create Cloud SQL instance
gcloud sql instances create scholarsense-db \
    --database-version=POSTGRES_15 \
    --tier=db-n1-standard-2 \
    --region=us-central1

# Create database
gcloud sql databases create chromadb \
    --instance=scholarsense-db
```

Then update backend to use Cloud SQL instead of local ChromaDB.

### 10. Set Up Monitoring

```bash
# Enable GCP monitoring
gcloud services enable monitoring.googleapis.com
gcloud services enable logging.googleapis.com

# Or install Prometheus/Grafana
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm install prometheus prometheus-community/kube-prometheus-stack -n monitoring --create-namespace
```

## Migration Checklist

- [ ] Create GCP project and enable billing
- [ ] Create GKE cluster
- [ ] Push images to GCR
- [ ] Update image references in deployments
- [ ] Create GCP-specific storage classes
- [ ] Deploy to GKE
- [ ] Set up LoadBalancer service
- [ ] Configure domain DNS
- [ ] Install nginx-ingress-controller
- [ ] Set up SSL with cert-manager
- [ ] Configure monitoring
- [ ] Set up automated backups for PVCs
- [ ] Configure IAM roles and service accounts
- [ ] Set up CI/CD pipeline (Cloud Build or GitHub Actions)

## Cost Optimization

1. **Use Preemptible Nodes**: Save up to 80%
   ```bash
   gcloud container node-pools create preemptible-pool \
       --cluster=scholarsense-cluster \
       --preemptible \
       --num-nodes=2
   ```

2. **Autoscaling**: Only pay for what you use
   ```bash
   kubectl autoscale deployment backend -n scholarsense --min=1 --max=5 --cpu-percent=70
   ```

3. **Use Cloud Storage for uploads** instead of PVCs:
   - Install `google-cloud-storage` Python package
   - Update backend to use GCS bucket
   - Much cheaper than persistent disks

4. **Use Cloud CDN**: Cache frontend static assets

## Automation: CI/CD with Cloud Build

**cloudbuild.yaml**:
```yaml
steps:
  # Build backend
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'gcr.io/$PROJECT_ID/backend:$SHORT_SHA', './apps/backend']
  
  # Build frontend
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'gcr.io/$PROJECT_ID/frontend:$SHORT_SHA', './apps/frontend']
  
  # Push images
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'gcr.io/$PROJECT_ID/backend:$SHORT_SHA']
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'gcr.io/$PROJECT_ID/frontend:$SHORT_SHA']
  
  # Deploy to GKE
  - name: 'gcr.io/cloud-builders/kubectl'
    args:
      - 'set'
      - 'image'
      - 'deployment/backend'
      - 'backend=gcr.io/$PROJECT_ID/backend:$SHORT_SHA'
      - '-n'
      - 'scholarsense'
    env:
      - 'CLOUDSDK_COMPUTE_ZONE=us-central1-a'
      - 'CLOUDSDK_CONTAINER_CLUSTER=scholarsense-cluster'

images:
  - 'gcr.io/$PROJECT_ID/backend:$SHORT_SHA'
  - 'gcr.io/$PROJECT_ID/frontend:$SHORT_SHA'
```

## Comparison: Minikube vs GKE

| Feature | Minikube (Local) | GKE (Production) |
|---------|-----------------|------------------|
| **Same manifests?** | ✅ Yes | ✅ Yes |
| **kubectl commands?** | ✅ Same | ✅ Same |
| **Networking** | Limited | Full LoadBalancer support |
| **Storage** | HostPath/Local | GCE Persistent Disks (SSD) |
| **Scaling** | Manual | Autoscaling |
| **High Availability** | No | Yes (multi-zone) |
| **SSL/TLS** | Manual | Automatic (cert-manager) |
| **Cost** | Free | ~$200-500/month |
| **Access** | localhost:30000 | yourdomain.com (HTTPS) |

## Key Takeaway

**The beauty of Kubernetes**: You develop locally with Minikube using the same manifests, then deploy to production (GKE) with minimal changes:

1. ✅ Update image URLs (local → GCR)
2. ✅ Change `imagePullPolicy: Never` → `Always`
3. ✅ Change Service `NodePort` → `LoadBalancer`
4. ✅ Add production storage classes

Everything else stays **exactly the same**! 🎉
