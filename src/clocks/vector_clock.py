from src.config.settings import settings
from typing import Dict
from src.utils.VectorClockComparison import VectorClockComparison

class VectorClock:
    def __init__(self):
        self.node_id = settings.NODE_ID
        self.clock: Dict[str, int] = {}
        for peer in settings.ALL_PEERS:
            if peer != self.node_id:
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
        elif isRemoteNodeGreater and not isLocalNodeGreater:
            return VectorClockComparison.LESS_THAN
        if isLocalNodeGreater and isRemoteNodeGreater:
            return VectorClockComparison.CONCURRENT
        return VectorClockComparison.EQUAL

    def to_dict(self) -> Dict[str, int]:
        return self.clock.copy()

    @classmethod
    def from_dict(cls, node_id: str, clock_dict: Dict[str, int]):
        vc = cls(node_id)
        vc.clock = clock_dict.copy()
        return vc