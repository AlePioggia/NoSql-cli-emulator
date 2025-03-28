API_NODE1="http://localhost:8001"
API_NODE2="http://localhost:8002"
API_NODE3="http://localhost:8003"

TEST_KEY="gossip_test_key"
TEST_VALUE="gossip_test_value"

echo "Waiting for API to start..."
sleep 5  

test_api() {
    local endpoint=$1
    local method=$2
    local data=$3
    local node_url=$4

    if [ "$method" == "POST" ]; then
        response=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$node_url$endpoint" -H "Content-Type: application/json" -d "$data")
    elif [ "$method" == "GET" ]; then
        response=$(curl -s -X GET "$node_url$endpoint")
    fi

    echo "$response"
}

echo "Testing Gossip Propagation"

echo "Setting key on Node 1..."
test_api "/set/$TEST_KEY" "POST" "{\"value\": \"$TEST_VALUE\"}" "$API_NODE1"

echo "Waiting for gossip propagation..."
sleep 10 

echo "Checking key on all nodes..."
node1_value=$(test_api "/get/$TEST_KEY" "GET" "" "$API_NODE1")
node2_value=$(test_api "/get/$TEST_KEY" "GET" "" "$API_NODE2")
node3_value=$(test_api "/get/$TEST_KEY" "GET" "" "$API_NODE3")

echo "🖥 Node 1: $node1_value"
echo "🖥 Node 2: $node2_value"
echo "🖥 Node 3: $node3_value"

if [[ "$node1_value" == "$node2_value" && "$node2_value" == "$node3_value" ]]; then
    echo "SUCCESS: Gossip propagation works!"
else
    echo "ERROR: Gossip propagation failed!"
fi

echo "Gossip test completed"
