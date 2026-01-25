# DevOps Web - Helm Chart

Helm chart pro nasazení Flask aplikace DevOps Web do Kubernetes.

## Prerekvizity

- Kubernetes cluster (1.19+)
- Helm 3.x
- kubectl nakonfigurován
- Nginx Ingress Controller
- Cert-manager pro SSL certifikáty (volitelné)

## Instalace

### 1. Build a push Docker image

```bash
# Build image
docker build -t your-registry/devops-web:1.0.0 .

# Push do registry
docker push your-registry/devops-web:1.0.0
```

### 2. Upravit values.yaml

```bash
cd helm
cp values.yaml values-prod.yaml
```

Uprav `values-prod.yaml`:
- `image.repository` - tvoje Docker registry
- `image.tag` - verze image
- `ingress.hosts[0].host` - tvoje doména
- `secrets.*` - všechny hesla a credentials

### 3. Instalace chartu

```bash
# Vytvoř namespace
kubectl create namespace devops-web

# Instalace s custom values
helm install devops-web ./helm \
  --namespace devops-web \
  --values helm/values-prod.yaml

# Nebo s inline hodnotami
helm install devops-web ./helm \
  --namespace devops-web \
  --set image.repository=your-registry/devops-web \
  --set image.tag=1.0.0 \
  --set ingress.hosts[0].host=devops.example.com \
  --set secrets.secretKey=your-secret-key \
  --set secrets.adminUser=admin \
  --set secrets.adminPass=secure-password \
  --set secrets.smtpUser=smtp@example.com \
  --set secrets.smtpPass=smtp-password \
  --set secrets.emailTo=you@example.com
```

### 4. Kontrola stavu

```bash
# Sleduj pody
kubectl get pods -n devops-web -w

# Zkontroluj service
kubectl get svc -n devops-web

# Zkontroluj ingress
kubectl get ingress -n devops-web

# Logy
kubectl logs -n devops-web -l app.kubernetes.io/name=devops-web -f
```

## Upgrade

```bash
# Update values nebo image tag
helm upgrade devops-web ./helm \
  --namespace devops-web \
  --values helm/values-prod.yaml

# S novou verzí image
helm upgrade devops-web ./helm \
  --namespace devops-web \
  --set image.tag=1.1.0 \
  --reuse-values
```

## Uninstall

```bash
helm uninstall devops-web --namespace devops-web
kubectl delete namespace devops-web
```

## Konfigurace

### Základní hodnoty

| Parametr | Popis | Default |
|----------|-------|---------|
| `replicaCount` | Počet replik | `2` |
| `image.repository` | Docker image repository | `your-registry/devops-web` |
| `image.tag` | Image tag | `latest` |
| `service.type` | Kubernetes service type | `ClusterIP` |
| `service.port` | Service port | `80` |

### Persistence

| Parametr | Popis | Default |
|----------|-------|---------|
| `persistence.enabled` | Zapnout persistent volume | `true` |
| `persistence.size` | Velikost disku | `1Gi` |
| `persistence.storageClass` | Storage class | `""` (default) |
| `persistence.mountPath` | Cesta pro mount | `/app/data` |

### Ingress

| Parametr | Popis | Default |
|----------|-------|---------|
| `ingress.enabled` | Zapnout ingress | `true` |
| `ingress.className` | Ingress class | `nginx` |
| `ingress.hosts[0].host` | Hostname | `devops.example.com` |
| `ingress.tls[0].secretName` | TLS secret | `devops-web-tls` |

### Secrets

| Parametr | Popis |
|----------|-------|
| `secrets.secretKey` | Flask SECRET_KEY |
| `secrets.adminUser` | Admin username |
| `secrets.adminPass` | Admin heslo |
| `secrets.smtpUser` | SMTP uživatel |
| `secrets.smtpPass` | SMTP heslo |
| `secrets.emailTo` | Email pro notifikace |

### Resources

```yaml
resources:
  limits:
    cpu: 500m
    memory: 512Mi
  requests:
    cpu: 100m
    memory: 128Mi
```

### Autoscaling

```yaml
autoscaling:
  enabled: false
  minReplicas: 2
  maxReplicas: 10
  targetCPUUtilizationPercentage: 80
```

## Příklady použití

### Production s Let's Encrypt

```bash
helm install devops-web ./helm \
  --namespace production \
  --create-namespace \
  --set image.repository=registry.example.com/devops-web \
  --set image.tag=v1.0.0 \
  --set ingress.hosts[0].host=devops.example.com \
  --set ingress.annotations."cert-manager\.io/cluster-issuer"=letsencrypt-prod \
  --set secrets.secretKey=$(openssl rand -base64 32) \
  --set secrets.adminUser=admin \
  --set secrets.adminPass=$(openssl rand -base64 16)
```

### Development bez TLS

```bash
helm install devops-web ./helm \
  --namespace dev \
  --create-namespace \
  --set ingress.tls={} \
  --set replicaCount=1 \
  --set resources.requests.cpu=50m \
  --set resources.requests.memory=64Mi
```

### S external secrets operator

```yaml
# values-prod.yaml
secrets:
  # Ponechat prázdné - použije external-secrets
  secretKey: ""
  adminUser: ""
  adminPass: ""
  
# Vytvořit ExternalSecret manifest
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: devops-web
spec:
  refreshInterval: 1h
  secretStoreRef:
    name: vault-backend
    kind: SecretStore
  target:
    name: devops-web
    creationPolicy: Owner
  data:
  - secretKey: SECRET_KEY
    remoteRef:
      key: devops-web/secret-key
```

## Troubleshooting

### Pody se nespouštějí

```bash
# Zkontroluj events
kubectl describe pod -n devops-web -l app.kubernetes.io/name=devops-web

# Zkontroluj logy
kubectl logs -n devops-web -l app.kubernetes.io/name=devops-web --previous
```

### Database problémy

```bash
# Zkontroluj PVC
kubectl get pvc -n devops-web

# Exec do podu
kubectl exec -it -n devops-web deployment/devops-web -- /bin/sh
ls -la /app/data
```

### Ingress nefunguje

```bash
# Zkontroluj ingress controller logy
kubectl logs -n ingress-nginx -l app.kubernetes.io/component=controller

# Ověř DNS
nslookup devops.example.com

# Test z clusteru
kubectl run -it --rm debug --image=curlimages/curl --restart=Never -- \
  curl -v http://devops-web.devops-web.svc.cluster.local
```

## CI/CD

### GitHub Actions příklad

```yaml
name: Deploy to Kubernetes

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Build and push
        run: |
          docker build -t ${{ secrets.REGISTRY }}/devops-web:${{ github.sha }} .
          docker push ${{ secrets.REGISTRY }}/devops-web:${{ github.sha }}
      
      - name: Deploy with Helm
        run: |
          helm upgrade --install devops-web ./helm \
            --namespace production \
            --set image.tag=${{ github.sha }} \
            --wait
```

## Monitoring

Pro monitoring přidej ServiceMonitor:

```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: devops-web
spec:
  selector:
    matchLabels:
      app.kubernetes.io/name: devops-web
  endpoints:
  - port: http
    path: /metrics
```
