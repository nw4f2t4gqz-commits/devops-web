#!/bin/bash
# Automatická konfigurace Nginx Proxy Manager přes API

set -e

NGINX_HOST="localhost:81"
DOMAIN="devops.itsvet.net"
FORWARD_HOST="devops-web-web-1"
FORWARD_PORT="5001"
EMAIL="your-email@example.com"

# Default credentials pro Nginx Proxy Manager
NPM_USER="admin@example.com"
NPM_PASS="changeme"

echo "🔧 Konfigurace Nginx Proxy Manager..."

# 1. Přihlášení a získání tokenu
echo "📝 Přihlašování..."
TOKEN=$(curl -s -X POST "http://${NGINX_HOST}/api/tokens" \
  -H "Content-Type: application/json" \
  -d "{\"identity\":\"${NPM_USER}\",\"secret\":\"${NPM_PASS}\"}" | jq -r '.token')

if [ "$TOKEN" = "null" ] || [ -z "$TOKEN" ]; then
  echo "❌ Chyba: Nelze se přihlásit do Nginx Proxy Manager"
  echo "   Zkontroluj credentials v UI nebo změň heslo ze 'changeme'"
  exit 1
fi

echo "✅ Přihlášení úspěšné"

# 2. Zkontroluj, jestli proxy host už existuje
echo "🔍 Kontrola existujícího Proxy Host..."
EXISTING_HOST=$(curl -s -X GET "http://${NGINX_HOST}/api/nginx/proxy-hosts" \
  -H "Authorization: Bearer ${TOKEN}" | jq -r ".[] | select(.domain_names[] == \"${DOMAIN}\") | .id")

if [ -n "$EXISTING_HOST" ]; then
  echo "✅ Proxy Host pro ${DOMAIN} již existuje (ID: ${EXISTING_HOST})"
  exit 0
fi

# 3. Vytvoř nový Proxy Host
echo "➕ Vytvářím nový Proxy Host..."
RESPONSE=$(curl -s -X POST "http://${NGINX_HOST}/api/nginx/proxy-hosts" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d "{
    \"domain_names\": [\"${DOMAIN}\"],
    \"forward_scheme\": \"http\",
    \"forward_host\": \"${FORWARD_HOST}\",
    \"forward_port\": ${FORWARD_PORT},
    \"certificate_id\": 0,
    \"ssl_forced\": 0,
    \"caching_enabled\": true,
    \"block_exploits\": true,
    \"allow_websocket_upgrade\": true,
    \"access_list_id\": 0,
    \"advanced_config\": \"\",
    \"enabled\": true,
    \"http2_support\": true,
    \"hsts_enabled\": true,
    \"hsts_subdomains\": false
  }")

HOST_ID=$(echo "$RESPONSE" | jq -r '.id')

if [ "$HOST_ID" = "null" ] || [ -z "$HOST_ID" ]; then
  echo "❌ Chyba při vytváření Proxy Host"
  echo "$RESPONSE"
  exit 1
fi

echo "✅ Proxy Host vytvořen (ID: ${HOST_ID})"

# 4. Vyžádej SSL certifikát (Let's Encrypt)
echo "🔒 Vyžadování SSL certifikátu..."
SSL_RESPONSE=$(curl -s -X POST "http://${NGINX_HOST}/api/nginx/certificates" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d "{
    \"domain_names\": [\"${DOMAIN}\"],
    \"meta\": {
      \"letsencrypt_email\": \"${EMAIL}\",
      \"letsencrypt_agree\": true,
      \"dns_challenge\": false
    },
    \"provider\": \"letsencrypt\"
  }")

CERT_ID=$(echo "$SSL_RESPONSE" | jq -r '.id')

if [ "$CERT_ID" != "null" ] && [ -n "$CERT_ID" ]; then
  echo "✅ SSL certifikát vytvořen (ID: ${CERT_ID})"
  
  # 5. Přiřaď SSL certifikát k Proxy Host
  echo "🔗 Přiřazování SSL certifikátu..."
  curl -s -X PUT "http://${NGINX_HOST}/api/nginx/proxy-hosts/${HOST_ID}" \
    -H "Authorization: Bearer ${TOKEN}" \
    -H "Content-Type: application/json" \
    -d "{
      \"domain_names\": [\"${DOMAIN}\"],
      \"forward_scheme\": \"http\",
      \"forward_host\": \"${FORWARD_HOST}\",
      \"forward_port\": ${FORWARD_PORT},
      \"certificate_id\": ${CERT_ID},
      \"ssl_forced\": 1,
      \"caching_enabled\": true,
      \"block_exploits\": true,
      \"allow_websocket_upgrade\": true,
      \"access_list_id\": 0,
      \"advanced_config\": \"\",
      \"enabled\": true,
      \"http2_support\": true,
      \"hsts_enabled\": true,
      \"hsts_subdomains\": false
    }" > /dev/null
  
  echo "✅ SSL certifikát přiřazen k ${DOMAIN}"
else
  echo "⚠️  SSL certifikát nelze vytvořit automaticky (možná už existuje nebo je potřeba DNS propagace)"
  echo "   Můžeš ho přidat manuálně v UI: http://${NGINX_HOST}"
fi

echo ""
echo "🎉 Konfigurace dokončena!"
echo "   Web by měl být dostupný na: https://${DOMAIN}"
