#!/bin/bash
# Minikube Setup Script pro DevOps Web

set -e

echo "🚀 DevOps Web - Minikube Setup"
echo "================================"

# 1. Start Minikube (pokud není spuštěný)
echo "📦 Checking Minikube status..."
if ! minikube status > /dev/null 2>&1; then
    echo "Starting Minikube..."
    minikube start --cpus=2 --memory=4096
else
    echo "✅ Minikube already running"
fi

# 2. Enable Ingress addon
echo "🌐 Enabling Ingress..."
minikube addons enable ingress

# 3. Build Docker image v Minikube
echo "🔨 Building Docker image..."
eval $(minikube docker-env)
docker build -t devops-web:latest .

# 4. Použij Helm chart z /tmp (workaround pro iCloud extended attributes)
echo "📦 Using Helm chart..."
HELM_LOCAL="/tmp/devops-web-chart"

if [ ! -d "$HELM_LOCAL" ]; then
    echo "❌ Helm chart not found at $HELM_LOCAL"
    echo "Creating chart from ./helm..."
    helm create "$HELM_LOCAL"
    rm -rf "$HELM_LOCAL/templates/tests" "$HELM_LOCAL/charts" "$HELM_LOCAL/templates/NOTES.txt"
    cp -R ./helm/templates/* "$HELM_LOCAL/templates/"
    cp ./helm/values*.yaml "$HELM_LOCAL/"
    cat > "$HELM_LOCAL/Chart.yaml" << 'EOF'
apiVersion: v2
name: devops-web
description: DevOps Web Application - Flask-based contact form and admin panel
type: application
version: 1.0.0
appVersion: "1.0.0"
EOF
fi

# 5. Deploy pomocí Helm
echo "📊 Deploying with Helm..."
kubectl create namespace devops-web --dry-run=client -o yaml | kubectl apply -f -

helm upgrade --install devops-web "$HELM_LOCAL" \
  --namespace devops-web \
  --values "$HELM_LOCAL/values-dev.yaml" \
  --wait

# 6. Cleanup
rm -rf "$HELM_LOCAL"

# 6. Cleanup
rm -rf "$HELM_LOCAL"

# 7. Čekej na ready
echo "⏳ Waiting for pods..."
kubectl wait --for=condition=ready pod \
  -l app.kubernetes.io/name=devops-web \
  -n devops-web \
  --timeout=300s

# 8. Získej Minikube IP
MINIKUBE_IP=$(minikube ip)
echo ""
echo "✅ Deployment complete!"
echo "================================"
echo "📍 Application URL: http://devops-web.local"
echo "🔧 Add to /etc/hosts:"
echo "   sudo echo '$MINIKUBE_IP devops-web.local' >> /etc/hosts"
echo ""
echo "📊 Useful commands:"
echo "   kubectl get pods -n devops-web"
echo "   kubectl logs -n devops-web -l app.kubernetes.io/name=devops-web -f"
echo "   kubectl port-forward -n devops-web svc/devops-web 8080:80"
echo "   minikube service devops-web -n devops-web"
echo ""
echo "🔗 Access via port-forward:"
echo "   kubectl port-forward -n devops-web svc/devops-web 8080:80"
echo "   Open: http://localhost:8080"
