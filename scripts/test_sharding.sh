#!/bin/bash

API_KEY="abcd1234-admin-2099-12-31"
HEADER_API_KEY="X-API-KEY: ${API_KEY}"

# node_number -> value
declare -A keys
keys=(
  [8001]="user_123" 
  [8002]="user_456"
  [8003]="user_789" 
)

# expected results
declare -A expected_values
expected_values=(
  [user_123]="Alice"
  [user_456]="Bob"
  [user_789]="Charlie"
)

echo "...Inserting keys..."
curl -s -X POST http://localhost:8001/set/user_123 -H "Content-Type: application/json" -H "$HEADER_API_KEY" -d '{"value": "Alice"}' > /dev/null
curl -s -X POST http://localhost:8002/set/user_456 -H "Content-Type: application/json" -H "$HEADER_API_KEY" -d '{"value": "Bob"}' > /dev/null
curl -s -X POST http://localhost:8003/set/user_789 -H "Content-Type: application/json" -H "$HEADER_API_KEY" -d '{"value": "Charlie"}' > /dev/null

echo "Wait for gossip propagation ..."
sleep 5

echo -e "\n starting test..."

success=true

for port in 8001 8002 8003; do
  key=${keys[$port]}
  expected=${expected_values[$key]}
  
  echo -e "\n [node $port] expected result $key → $expected)"
  
  raw_response=$(curl -s http://localhost:$port/get/$key -H "$HEADER_API_KEY")
  value=$(echo "$raw_response" | sed -n 's/.*"value"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p')

  if [ "$value" == "$expected" ]; then
    echo "$key present in $port with value: '$value'"
  else
    echo "Error: $key wrong value in node: $port"
    success=false
  fi

  for other_key in "${!expected_values[@]}"; do
    if [ "$other_key" != "$key" ]; then
            response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:$port/get/$other_key -H "$HEADER_API_KEY")
      if [ "$response" == "200" ]; then
        echo "Error: $other_key wasn't supposed to be saved on node: $port but it is"
        success=false
      else
        echo "Key: $other_key correctly not present in node: $port"
      fi
    fi
  done
done

echo -e "\n Global verification..."
for port in 8001 8002 8003; do
  echo -e "\nNode $port:"
  curl -s http://localhost:$port/keys -H "$HEADER_API_KEY"
  echo ""
done

if [ "$success" = true ]; then
  echo -e "\n Completed test: sharding works as expected."
  exit 0
else
  echo -e "\n Failed test: some keys (check logs) are not present in the expected nodes."
  exit 1
fi
