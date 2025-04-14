from src.utils.VectorClockComparison import VectorClockComparison
from src.clocks.vector_clock import VectorClock
from src.utils.VectorClockResponsState import VectorClockResponseState

def LWW_resolve_conflict(local_vc: VectorClock, remote_vc_dict: dict, local_value: str, remote_value: str) -> str:
    comparison = local_vc.compare_clocks(remote_vc_dict)
    if comparison == VectorClockComparison.LESS_THAN:
        return VectorClockResponseState.ACCEPT
    elif comparison == VectorClockComparison.GREATER_THAN:
        return VectorClockResponseState.REJECT
    else:
        if sum(remote_vc_dict.values()) > sum(local_vc.clock.values()):
            return VectorClockResponseState.ACCEPT
        elif sum(remote_vc_dict.values()) < sum(local_vc.clock.values()):
            return VectorClockResponseState.REJECT
        else:
            return VectorClockResponseState.ACCEPT if remote_value > local_value else VectorClockResponseState.REJECT