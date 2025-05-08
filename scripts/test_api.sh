
API_URL="http://localhost:8001"
API_KEY="abc123ef-admin-2025-12-31"

echo "Waiting for API to start..."
until curl -s -H "X-API-KEY: $API_KEY" "$API_URL/keys" > /dev/null; do
    sleep 3 
done

test_api() {
    local endpoint=$1
    local method=$2
    local data=$3

    if [ "$method" == "POST" ]; then
        response=$(curl -s -X POST "$API_URL$endpoint" -H "Content-Type: application/json" -H "X-API-KEY: $API_KEY" -d "$data" -w "\nHTTP_STATUS:%{http_code}")
    elif [ "$method" == "GET" ]; then
        response=$(curl -s -X GET "$API_URL$endpoint" -H "X-API-KEY: $API_KEY" -w "\nHTTP_STATUS:%{http_code}")
    elif [ "$method" == "DELETE" ]; then
        response=$(curl -s -X DELETE "$API_URL$endpoint" -H "X-API-KEY: $API_KEY" -w "\nHTTP_STATUS:%{http_code}")
    else
        echo "Unsupported HTTP method: $method"
        exit 1
    fi

    http_code=$(echo "$response" | grep "HTTP_STATUS" | awk -F':' '{print $2}')
    response_body=$(echo "$response" | sed 's/HTTP_STATUS:[0-9]*//')

    echo "Response body: $response_body"

    if [ "$http_code" -eq 200 ]; then
        echo "SUCCESS: $method $endpoint"
    else
        echo "ERROR: $method $endpoint - HTTP Status: $http_code"
    fi
}

echo "Running API tests..."

test_api "/set/testkey" "POST" '{"value": "testvalue"}'

test_api "/get/testkey" "GET"

test_api "/keys" "GET"

test_api "/delete/testkey" "DELETE"

echo "Tests completed!"

