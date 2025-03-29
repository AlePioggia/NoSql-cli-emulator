#!/bin/bash

API_NODE1="http://localhost:8001"
API_NODE2="http://localhost:8002"
API_NODE3="http://localhost:8003"

echo "🔄 Waiting for API to start..."
sleep 5 
write_to_node() {
    local node_url=$1
    local key=$2
    local value=$3

    response=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$node_url/set/$key" -H "Content-Type: application/json" -d "{\"value\": \"$value\"}")

    if [ "$response" -eq 200 ]; then
        echo "SUCCESS: Wrote ($key, $value) to $node_url"
    else
        echo "ERROR: Failed to write to $node_url - HTTP Status: $response"
    fi
}

echo "Writing data to nodes..."

write_to_node "$API_NODE1" "key1" "value1_from_node1"
write_to_node "$API_NODE2" "key2" "value2_from_node2"
write_to_node "$API_NODE3" "key3" "value3_from_node3"

echo "All write operations completed!"
