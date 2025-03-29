from dataclasses import dataclass, field
from typing import Dict
import json

@dataclass
class Gossip:
    gossip_id: str
    peer: str

@dataclass
class Node:
    sent_gossips: Dict[str, Gossip] = field(default_factory=dict) 
    received_gossips: Dict[str, Gossip] = field(default_factory=dict)

@dataclass
class GossipNetwork:
    nodes: Dict[str, Node] = field(default_factory=dict)

    def add_node(self, node_name: str):
        if node_name not in self.nodes:
            self.nodes[node_name] = Node()

    def add_sent_gossip(self, node_name: str, gossip_id: str, peer: str):
        if node_name in self.nodes:
            node = self.nodes[node_name]
            node.sent_gossips[gossip_id] = Gossip(gossip_id, peer)

    def add_received_gossip(self, node_name: str, gossip_id: str, peer: str):
        if node_name in self.nodes:
            node = self.nodes[node_name]
            node.received_gossips[gossip_id] = Gossip(gossip_id, peer)

    def get_node_info(self, node_name: str):
        if node_name in self.nodes:
            return self.nodes[node_name]
        
    def get_all_nodes(self):
        return self.nodes.keys()
    
    def get_sent_gossips(self, node_name: str):
        if node_name in self.nodes:
            return self.nodes[node_name].sent_gossips.values()
        
    def get_received_gossips(self, node_name: str):
        if node_name in self.nodes:
            return self.nodes[node_name].received_gossips.values()
        
    def filter_peers(self, peers: list, gossip_id: str, node_name: str):
        return [
            peer
            for peer in peers
            if (
                peer not in self.nodes
                or gossip_id not in self.nodes[peer].received_gossips
                and gossip_id not in self.nodes[node_name].sent_gossips
            )
        ]


    def binaryEncode(self, gossip_id: str):
        return gossip_id.encode('utf-8')
    
    def binaryDecode(self, gossip_id: bytes):
        return gossip_id.decode('utf-8')
    
    def serialize(self):
        return json.dumps({
            "nodes": {
                node_name: {
                    "sent_gossips": {
                        gossip_id: {"gossip_id": gossip.gossip_id, "peer": gossip.peer} 
                        for gossip_id, gossip in node.sent_gossips.items()
                    },
                    "received_gossips": {
                        gossip_id: {"gossip_id": gossip.gossip_id, "peer": gossip.peer} 
                        for gossip_id, gossip in node.received_gossips.items()
                    }
                } 
                for node_name, node in self.nodes.items()
            }
        })

    @staticmethod
    def deserialize(serialized_network: str):
        data = json.loads(serialized_network)
        network = GossipNetwork()
        for node_name, node_data in data["nodes"].items():
            network.add_node(node_name)
            for gossip_id, gossip_data in node_data["sent_gossips"].items():
                network.add_sent_gossip(node_name, gossip_data["gossip_id"], gossip_data["peer"])
            for gossip_id, gossip_data in node_data["received_gossips"].items():
                network.add_received_gossip(node_name, gossip_data["gossip_id"], gossip_data["peer"])
        return network

    def update_network(self, other_network: 'GossipNetwork'):
        for node_name, other_node in other_network.nodes.items():
            if node_name not in self.nodes:
                self.add_node(node_name)
            for gossip_id, gossip in other_node.sent_gossips.items():
                self.add_sent_gossip(node_name, gossip.gossip_id, gossip.peer)
            for gossip_id, gossip in other_node.received_gossips.items():
                self.add_received_gossip(node_name, gossip.gossip_id, gossip.peer)

    def __str__(self):
        return str(self.nodes)
