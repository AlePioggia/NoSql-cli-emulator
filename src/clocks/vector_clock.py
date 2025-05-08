from typing import Dict
from src.utils.VectorClockComparison import VectorClockComparison
import os

class VectorClock:
    def __init__(self):
        self.node_id = os.getenv("NODE_ID", "1")
        self.clock: Dict[str, int] = {}
        all_peers_id = os.getenv("ALL_PEERS_IDS", "1,2,3").split(",")
        for peer in all_peers_id:
            self.clock[peer] = 0

    def increment(self):
        self.clock[self.node_id] = self.clock.get(self.node_id, 0) + 1
    
    def update(self, received_clock: Dict[str, int]):
        for node, counter in received_clock.items():
            self.clock[node] = max(self.clock.get(node, 0), counter)
        self.increment()

    def compare_clocks(self, compared_clock: Dict[str, int]) -> VectorClockComparison:
        isLocalNodeGreater, isRemoteNodeGreater = False, False
        
        if len(self.clock) != len(compared_clock):
            return VectorClockComparison.CONCURRENT

        for node in set(self.clock.keys() | set(compared_clock.keys())):
            local = self.clock.get(node, 0)
            remote = compared_clock.get(node, 0)
            if local > remote:
                isLocalNodeGreater = True
            elif local < remote:
                isRemoteNodeGreater = True
            
        if isLocalNodeGreater and not isRemoteNodeGreater:
            return VectorClockComparison.GREATER_THAN
        if isRemoteNodeGreater and not isLocalNodeGreater:
            return VectorClockComparison.LESS_THAN
        if isLocalNodeGreater and isRemoteNodeGreater:
            return VectorClockComparison.CONCURRENT
        return VectorClockComparison.EQUAL

    def to_dict(self) -> Dict[str, int]:
        return self.clock.copy()

    @classmethod
    def from_dict(cls, node_id: str, clock_dict: Dict[str, int]):
        vc = cls()
        vc.clock = clock_dict.copy()
        vc.node_id = node_id
        return vc
    
    def create_vector_from_dict(self, clock_dict: Dict[str, int]):
        self.clock = clock_dict
        return self