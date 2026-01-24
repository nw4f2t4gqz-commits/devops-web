# Deployment Setup - GitHub Actions → VPS Server

## 1. Generování SSH klíče (pokud ještě nemáš)

```bash
# Na tvém lokálním počítači
ssh-keygen -t ed25519 -C "github-actions" -f ~/.ssh/github_actions_key

# Zkopíruj PUBLIC klíč na VPS server
ssh-copy-id -i ~/.ssh/github_actions_key.pub username@tvuj-vps-server

# Nebo manuálně:
cat ~/.ssh/github_actions_key.pub
# Zkopíruj výstup a přidej ho na VPS do ~/.ssh/authorized_keys
```

## 2. Nastavení GitHub Secrets

Jdi na: https://github.com/nw4f2t4gqz-commits/devops-web/settings/secrets/actions

### Potřebné Secrets:

#### VPS_HOST
```
123.45.67.89  # IP adresa tvého VPS (nebo vps.example.com)
```

#### VPS_USERNAME
```
root  # nebo ubuntu, debian, atd. (podle VPS poskytovatele)
```

#### VPS_SSH_KEY
```bash
# Zkopíruj PRIVATE klíč (celý soubor!)
cat ~/.ssh/github_actions_key
# Zkopíruj celý výstup včetně:
# -----BEGIN OPENSSH PRIVATE KEY-----
# ...
# -----END OPENSSH PRIVATE KEY-----
```

#### VPS_PORT (volitelné)
```
22  # standardní SSH port (nebo vlastní, pokud jsi změnil)
```

#### SECRET_KEY
```
# Vygeneruj silný secret key:
python3 -c "import secrets; print(secrets.token_hex(32))"
```

## 3. Test připojení

```bash
# Otestuj SSH připojení na VPS
ssh -i ~/.ssh/github_actions_key username@tvuj-vps-ip

# Na VPS zkontroluj Docker
docker ps
docker info
```

## 4. Příprava VPS serveru

```bash
# Přihlas se na VPS
ssh username@tvuj-vps-ip

# Nainstaluj Docker (pokud ještě není)
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Přidej uživatele do docker group
sudo usermod -aG docker $USER
newgrp docker

# Otestuj Docker
docker ps
```

## 5. Spuštění deploymentu

### Automaticky:
- Push do `main` branch automaticky spustí build a deploy

```bash
git add .
git commit -m "feat: přidány články"
git push origin main
```

### Manuálně:
- Jdi na: https://github.com/nw4f2t4gqz-commits/devops-web/actions
- Klikni na "Docker Build & Publish"
- Klikni na "Run workflow"

## 6. Monitoring

### Zkontroluj GitHub Actions:
https://github.com/nw4f2t4gqz-commits/devops-web/actions

### Zkontroluj na VPS:
```bash
ssh username@tvuj-vps-ip

# Zkontroluj běžící containery
docker ps

# Zkontroluj logy
docker logs devops-web

# Otevři aplikaci
curl http://localhost:5000

# Zkontroluj z venku (nahraď IP_VPS svou IP)
curl http://IP_VPS:5000
```

## Troubleshooting

### SSH connection failed
```bash
# Zkontroluj SSH klíč
ssh -v -i ~/.ssh/github_actions_key username@server

# Zkontroluj authorized_keys na serveru
cat ~/.ssh/authorized_keys
```

### Docker pull failed
```bash
# Přihlas se na serveru do GHCR
echo $GHCR_PAT | docker login ghcr.io -u github-username --password-stdin
```

### Container won't start
```bash
# Zkontroluj logy
docker logs devops-web

# Zkontroluj port conflicts
sudo netstat -tulpn | grep 5000
```

## Alternativní řešení

### Option 1: Docker Compose na serveru
Vytvoř docker-compose.yml na serveru a použij `docker-compose pull && docker-compose up -d`

### Option 2: Kubernetes
Deploy do Kubernetes clusteru místo Docker

### Option 3: Watchtower (automatické aktualizace)
```bash
docker run -d \
  --name watchtower \
  -v /var/run/docker.sock:/var/run/docker.sock \
  containrrr/watchtower \
  --interval 300 \
  devops-web
```

### Option 4: Portainer Webhook
Použij Portainer webhook pro automatické aktualizace
