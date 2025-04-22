#!/bin/bash

set -e

API_KEY="abcd1234-admin-2099-12-31"
HEADER_API_KEY="X-API-KEY: ${API_KEY}"

NODE1="http://localhost:8001"
NODE2="http://localhost:8002"
NODE3="http://localhost:8003"

echo "🟢 Setting initial value on node1..."
curl -s -X POST "$NODE1/set/test_key" \
  -H "Content-Type: application/json" \
  -H "$HEADER_API_KEY" \
  -d '{"value": "hello_from_node1"}'

echo "⏳ Waiting for gossip propagation..."
sleep 20

echo "🔍 Checking value on node2..."
VAL_NODE2=$(curl -s "$NODE2/get/test_key" \
  -H "$HEADER_API_KEY" \
  | grep -o '"value":"[^"]*"' | sed 's/"value":"//;s/"//')

if [ "$VAL_NODE2" = "hello_from_node1" ]; then
  echo "✅ Gossip propagated successfully!"
else
  echo "❌ ERROR: node2 has '$VAL_NODE2', expected 'hello_from_node1'"
  exit 1
fi

echo "⚠️ Triggering conflict on node3..."
curl -s -X POST "$NODE3/set/test_key" \
  -H "Content-Type: application/json" \
  -H "$HEADER_API_KEY" \
  -d '{"value": "conflict_from_node3"}'

echo "⏳ Waiting for conflict resolution..."
sleep 20

VAL1=$(curl -s "$NODE1/get/test_key" -H "$HEADER_API_KEY" | grep -o '"value":"[^"]*"' | sed 's/"value":"//;s/"//')
VAL2=$(curl -s "$NODE2/get/test_key" -H "$HEADER_API_KEY" | grep -o '"value":"[^"]*"' | sed 's/"value":"//;s/"//')
VAL3=$(curl -s "$NODE3/get/test_key" -H "$HEADER_API_KEY" | grep -o '"value":"[^"]*"' | sed 's/"value":"//;s/"//')

echo "📦 Final values:"
echo "  node1: $VAL1"
echo "  node2: $VAL2"
echo "  node3: $VAL3"

if [ "$VAL1" = "$VAL2" ] && [ "$VAL2" = "$VAL3" ]; then
  echo "✅ Conflict resolved with value: '$VAL1'"
else
  echo "❌ Nodes are not in sync:"
  echo "   node1: $VAL1"
  echo "   node2: $VAL2"
  echo "   node3: $VAL3"
  exit 1
fi

echo "✔️ Test completed successfully!"
