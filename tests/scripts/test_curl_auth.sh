#!/bin/bash

# Test auth endpoint with curl using proper HMAC signature
API_KEY="yQ1sz7kmNo35R94vlMx3mw"
API_SECRET="MBClYvt6hptvZTj6ZCDXWlS10je29EJjYKgRd78xX24"

# Generate timestamp
TIMESTAMP=$(date -u +%Y-%m-%dT%H:%M:%SZ)

# Request body
BODY='{"client_id":"test-client","permissions":["read","write"]}'

# Create message for signature
MESSAGE="${API_KEY}
${TIMESTAMP}
${BODY}"

# Generate HMAC signature
SIGNATURE=$(echo -n "$MESSAGE" | openssl dgst -sha256 -hmac "$API_SECRET" -binary | base64)

echo "Testing authentication with:"
echo "Timestamp: $TIMESTAMP"
echo "Signature: $SIGNATURE"
echo "Body: $BODY"
echo

# Make request with timeout
timeout 10 curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -H "X-Timestamp: $TIMESTAMP" \
  -H "X-Signature: $SIGNATURE" \
  -d "$BODY" \
  -v

echo
echo "Exit code: $?"