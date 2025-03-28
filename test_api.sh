API_URL="http://localhost:8001"

echo "Waiting for API to start..."
until curl -s "$API_URL/keys" > /dev/null; do
    sleep 2
done

test_api() {
    local endpoint=$1
    local method=$2
    local data=$3

    if [ "$method" == "POST" ]; then
        response=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$API_URL$endpoint" -H "Content-Type: application/json" -d "$data")
    elif [ "$method" == "GET" ]; then
        response=$(curl -s -o /dev/null -w "%{http_code}" -X GET "$API_URL$endpoint")
    elif [ "$method" == "DELETE" ]; then
        response=$(curl -s -o /dev/null -w "%{http_code}" -X DELETE "$API_URL$endpoint")
    else
        echo "Unsupported HTTP method: $method"
        exit 1
    fi

    if [ "$response" -eq 200 ]; then
        echo "SUCCESS: $method $endpoint"
    else
        echo "ERROR: $method $endpoint - HTTP Status: $response"
    fi
}

echo "Running API tests..."

test_api "/set/testkey" "POST" '{"value": "testvalue"}'

test_api "/get/testkey" "GET"

test_api "/keys" "GET"

test_api "/delete/testkey" "DELETE"

echo "tests completed!"
