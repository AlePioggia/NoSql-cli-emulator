API_KEY="abc123ef-admin-2025-12-31"
KEY="mykey"
VALUE="example_value"

curl -X POST "http://localhost:8001/set/${KEY}" \
  -H "Content-Type: application/json" \
  -H "X-API-KEY: ${API_KEY}" \
  -d "{\"value\": \"${VALUE}\"}"
