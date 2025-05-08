# NoSql-cli-emulator

Lightweight, distributed NoSQL emulator that implements sharding and replication using a peer-to-peer (P2P) architecture. The system will follow the BASE (Basically Available, Soft state, Eventually consistent) approach, ensuring high availability and reasonable fault tolerance while prioritizing low latency for read and write operations. It’s a cli application, interaction will be based on scripts or command line commands.

## User guide

Quick start guide for the **NoSql CLI Emulator** project.

### Prerequisites

- **Git**;
- **Docker** & **Docker compose**;

The sections below explain how to:

- Clone and set up the project;
- Start the environment with Docker Compose;  
- Run bash scripts;
- Interact with the API.

### 1. Clone and set up the project

```
git clone https://github.com/AlePioggia/NoSql-cli-emulator.git

cd NoSql-cli-emulator
```

### 2. Start the environment with Docker compose

The service supports a sharding switch, via the ENABLE_SHARDING environment variable, when true sharding is enabled, otherwise it won't be considered. So in order to run the docker containers, using docker-compose there are these two alternatives:

```
# Non-sharding mode
ENABLE_SHARDING=false docker-compose up

# Sharding mode
ENABLE_SHARDING=true docker-compose up
```

### 3. Run bash scripts 

The bash scripts, that interact with the service, can be run simply by executing:

#### With sharding enabled (ENABLE_SHARDING=true)

```
./test_sharding.sh
```

#### Without sharding (ENABLED_SHARDING=false)

```

# try out random insertions
./random_insertions.sh

# try gossip protocol
./test_gossip.sh

# try synchronization between peers
./test_synch.sh

# observe how a network partition is handled
./network_partitioning.sh

```

### 4. Interact with the API

The interaction with the API can be made through api requests, so in order to test it further or create custom bash scripts, the test_api_key.sh it's a working example of an working request.

```
API_KEY="abc123ef-admin-2025-12-31"
KEY="mykey"
VALUE="example_value"

curl -X POST "http://localhost:8001/set/${KEY}" \
  -H "Content-Type: application/json" \
  -H "X-API-KEY: ${API_KEY}" \
  -d "{\"value\": \"${VALUE}\"}"
```
