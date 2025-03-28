
- [Alessandro Pioggia](mailto:alessandro.pioggia2@studio.unibo.it)

### AI Disclaimer (if needed)

```
"During the preparation of this work, the author(s) used [NAME TOOL /
SERVICE] to [REASON].
After using this tool/service, the author(s) reviewed and edited the
content as needed and take(s) full responsibility for the content of the
final report/artifact."
```

## Abstract

The project goal is to develop a lightweight, distributed NoSQL emulator that implements sharding and replication using a peer-to-peer (P2P) architecture. The system will follow the BASE (Basically Available, Soft state, Eventually consistent) approach, ensuring high availability and reasonable fault tolerance while prioritizing low latency for read and write operations. It’s a cli application, interaction will be based on scripts or command line commands.

## Concept

Lightweight, distributed NoSQL emulator that implements sharding and replication using a peer-to-peer (P2P) architecture. The system will follow the BASE (Basically Available, Soft state, Eventually consistent) approach, ensuring high availability and reasonable fault tolerance while prioritizing low latency for read and write operations. It’s a cli application, interaction will be based on scripts or command line commands.

- Use case collection
    - _where_ are the users? 
    - _when_ and _how frequently_ do they interact with the system?
    - _how_ do they _interact_ with the system? which _devices_ are they using? pcs
    - does the system need to _store_ user's __data__? _which_? _where_?
    - most likely, there will be _multiple_ __roles__ 

# Requirements

## 1. Functional Requirements

### Requirement 1: Data Management
- **Description**: The system must allow storing, retrieving, modifying, and deleting data. Each operation must be performed through RESTful APIs.
- **Acceptance Criteria**:
  - The user should be able to make `POST`, `GET`, `PUT`, and `DELETE` requests to specific endpoints.
  - The operations for `set` and `get` should correctly store and retrieve data.
  - A `GET` request for a non-existent key should return a 404 error.

### Requirement 2: Gossip Protocol
- **Description**: The system must implement a gossip protocol mechanism that allows data replication between nodes. Nodes should be able to exchange updates periodically using a gossip strategy.
- **Acceptance Criteria**:
  - Each node must be capable of sending and receiving updates via the gossip protocol.
  - When a node receives an update, it must update its local state (memory).
  - Updates should be correctly synchronized between nodes, and the data must be identical across all nodes.
  - In the case of communication failures, nodes should attempt to re-establish the connection.

### Requirement 3: Heartbeat and Node Monitoring
- **Description**: The system must implement a heartbeat mechanism to monitor the health of nodes.
- **Acceptance Criteria**:
  - Each node should send regular heartbeat signals to confirm its availability.
  - The system should detect if any node is unresponsive or down and handle the situation by either retrying or marking it as unavailable.
  - Nodes should be able to adapt to the failure of other nodes, ensuring that data replication continues despite any node failures.

---

## 2. Non-Functional Requirements

### Requirement 4: Scalability
- **Description**: The system must be able to scale horizontally, meaning it should handle an increasing number of nodes and data volume without significant performance degradation.
- **Acceptance Criteria**:
  - The system should be able to add new nodes dynamically without disrupting existing operations.
  - The system should handle increased data volume efficiently.

### Requirement 5: Fault Tolerance
- **Description**: The system should be resilient to node failures and network issues, ensuring continued operation even in the presence of failures.
- **Acceptance Criteria**:
  - In case of node failure, the system should continue operating and retry data replication from the remaining nodes.
  - The system must recover gracefully from network partitions and re-sync data once the network is restored.

### Requirement 6: Availability
- **Description**: The system should ensure high availability, meaning the data should be accessible even if some of the nodes are unavailable.
- **Acceptance Criteria**:
  - At least one node should always be available to serve read and write requests.
  - If one or more nodes go down, the system should still function, ensuring the availability of data through other nodes.

---

## 3. Implementation Requirements

### Requirement 7: Programming Language and Framework
- **Description**: The system must be implemented using Python, with the FastAPI framework for the API layer.
- **Acceptance Criteria**:
  - The application must be written in Python and use FastAPI for building the web services.
  - All components of the system must comply with Python's best practices, including code style and modularity.

### Requirement 8: Dockerization
- **Description**: The system must be containerized using Docker to ensure easy deployment and scaling.
- **Acceptance Criteria**:
  - A Dockerfile must be provided to build and run the application.
  - The application should be able to run in a Docker container without any manual setup outside the container.
  - The system must work in a distributed environment using Docker Compose or similar tools for orchestration.

---

## 4. Glossary of Terms

- **Node**: A server or instance that participates in the distributed system, either providing or consuming services.
- **Gossip Protocol**: A communication protocol in which nodes periodically exchange information to propagate updates and synchronize data across the network.
- **Heartbeat**: A signal sent by a node to indicate its status (alive or down) in the system.
- **Replication**: The process of copying data from one node to another to ensure data consistency and availability across the system.

## Design

This chapter explains the strategies used to meet the requirements identified in the analysis.
Ideally, the design should be the same, regardless of the technological choices made during the implementation phase.

> You can re-order the sections as you prefer, but all the sections must be present in the end

### Architecture

- Which architectural style? 
    + why?

### Infrastructure

- are there _infrastructural components_ that need to be introduced? _how many_?
    * e.g. _clients_, _servers_, _load balancers_, _caches_, _databases_, _message brokers_, _queues_, _workers_, _proxies_, _firewalls_, _CDNs_, _etc._

- how do components	_distribute_ over the network? _where_?
    * e.g. do servers / brokers / databases / etc. sit on the same machine? on the same network? on the same datacenter? on the same continent?

- how do components _find_ each other?
    * how to _name_ components?
    * e.g. DNS, _service discovery_, _load balancing_, _etc._

> Component diagrams are welcome here

### Modelling

- which __domain entities__ are there?
    * e.g. _users_, _products_, _orders_, _etc._

- how do _domain entities_ __map to__ _infrastructural components_?
    * e.g. state of a video game on central server, while inputs/representations on clients
    * e.g. where to store messages in an IM app? for how long?

- which __domain events__ are there?
    * e.g. _user registered_, _product added to cart_, _order placed_, _etc._

- which sorts of __messages__ are exchanged?
    * e.g. _commands_, _events_, _queries_, _etc._

- what information does the __state__ of the system comprehend
    * e.g. _users' data_, _products' data_, _orders' data_, _etc._

> Class diagram are welcome here

### Interaction

- how do components _communicate_? _when_? _what_? 
- _which_ __interaction patterns__ do they enact?

> Sequence diagrams are welcome here

### Behaviour

- how does _each_ component __behave__ individually (e.g. in _response_ to _events_ or messages)?
    * some components may be _stateful_, others _stateless_

- which components are in charge of updating the __state__ of the system? _when_? _how_?

> State diagrams are welcome here

### Data and Consistency Issues

- Is there any data that needs to be stored?
    * _what_ data? _where_? _why_?

- how should _persistent data_ be __stored__?
    * e.g. relations, documents, key-value, graph, etc.
    * why?

- Which components perform queries on the database?
    * _when_? _which_ queries? _why_?
    * concurrent read? concurrent write? why?

- Is there any data that needs to be shared between components?
    * _why_? _what_ data?

### Fault-Tolerance

- Is there any form of data __replication__ / federation / sharing?
    * _why_? _how_ does it work?