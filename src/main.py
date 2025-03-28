import os
import uvicorn
from network.api_server import app
from network.gossip import GossipManager

# for local testing purposes
def get_peer_list():
     return [
        "http://node1:8000",
        "http://node2:8000",
        "http://node3:8000"
    ]

if __name__ == "__main__":
    peers = get_peer_list()

    app.state.gossip_manager = GossipManager(peers=peers, interval=5)
    app.state.gossip_manager.start()

    uvicorn.run(app, host="0.0.0.0", port=8000)