import pytest
from src.utils.VectorClockComparison import VectorClockComparison
from src.utils.VectorClockResponsState import VectorClockResponseState
from src.clocks.vector_clock import VectorClock
from src.clocks.conflict_resolver import LWW_resolve_conflict

@pytest.mark.parametrize("local_vc_dict, remote_vc_dict, local_value, remote_value, expected_response", [
    ({"node-1": 1, "node-2": 1, "node-3": 1}, {"node-1": 1, "node-2": 1, "node-3": 1}, "local_value", "remote_value", VectorClockResponseState.ACCEPT),
    ({"node-1": 1, "node-2": 1, "node-3": 1}, {"node-1": 2, "node-2": 2, "node-3": 2}, "local_value", "local_value", VectorClockResponseState.ACCEPT),
    ({"node-1": 2, "node-2": 2, "node-3": 2}, {"node-1": 1, "node-2": 1, "node-3": 1}, "remote_value", "local_value", VectorClockResponseState.REJECT),
])
def test_lww_resolve_conflict_concurrent(local_vc_dict, remote_vc_dict, local_value, remote_value, expected_response):
    local_vc = VectorClock()
    local_vc.clock = local_vc_dict
    local_vc.node_id = "node-1"
    remote_vc = remote_vc_dict
    response = LWW_resolve_conflict(local_vc, remote_vc, local_value, remote_value)

    assert response == expected_response
