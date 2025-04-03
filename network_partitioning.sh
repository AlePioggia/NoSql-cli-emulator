API_NODE1="http://localhost:8001"
API_NODE2="http://localhost:8002"
API_NODE3="http://localhost:8003"

TEST_KEY="partition_key"
VALUE_NODE1="value_from_node1"
VALUE_NODE3="value_from_node3"

echo "Waiting for API nodes to start..."
until curl -s "$API_NODE1/keys" | grep -q "keys"; do
    sleep 2
done
echo "Nodes appear to be up."

echo "Simulating network partition: disconnecting node3 from the network..."
docker network disconnect nosql-cli-emulator_gossip_network node3

sleep 3

echo "Updating key on partition1 (node1)..."
curl -s -X POST "$API_NODE1/set/$TEST_KEY" -H "Content-Type: application/json" -d "{\"value\": \"$VALUE_NODE1\"}"
echo "Updating key on partition2 (node3)..."
curl -s -X POST "$API_NODE3/set/$TEST_KEY" -H "Content-Type: application/json" -d "{\"value\": \"$VALUE_NODE3\"}"

echo "Waiting for local propagation within each partition..."
sleep 15

echo "Checking key on node1 (expected: $VALUE_NODE1):"
curl -s "$API_NODE1/get/$TEST_KEY"
echo ""
echo "Checking key on node3 (expected: $VALUE_NODE3):"
curl -s "$API_NODE3/get/$TEST_KEY"
echo ""

echo "Reconnecting node3 to the network..."
docker network connect nosql-cli-emulator_gossip_network node3

echo "Waiting for eventual consistency to converge..."
sleep 30

echo "Final state of key '$TEST_KEY':"
echo "Node1:"
curl -s "$API_NODE1/get/$TEST_KEY"
echo ""
echo "Node2:"
curl -s "$API_NODE2/get/$TEST_KEY"
echo ""
echo "Node3:"
curl -s "$API_NODE3/get/$TEST_KEY"
echo ""

echo "Test completed!"
