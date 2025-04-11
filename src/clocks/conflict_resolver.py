from src.utils.VectorClockComparison import VectorClockComparison
from src.clocks.vector_clock import VectorClock
from src.utils.VectorClockResponsState import VectorClockResponseState

def LWW_resolve_conflict(local_vc: VectorClock, remote_vc_dict: dict, local_value: str, remote_value: str) -> str:
    comparison = local_vc.compare_clocks(remote_vc_dict)
    if comparison == VectorClockComparison.LESS_THAN:
        return VectorClockResponseState.ACCEPT
    elif comparison == VectorClockComparison.GREATER_THAN:
        return VectorClockResponseState.REJECT
    elif comparison == VectorClockComparison.CONCURRENT:
        return VectorClockResponseState.ACCEPT if hash(remote_value) > hash(local_value) else VectorClockResponseState.REJECT
    elif comparison == VectorClockComparison.EQUAL:
        return VectorClockResponseState.NO_OP
    return VectorClockResponseState.NO_OP