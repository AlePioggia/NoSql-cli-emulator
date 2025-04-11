from src.clocks.vector_clock import VectorClock
from src.utils.VectorClockComparison import VectorClockComparison
import pytest 
from typing import Dict
from src.config import settings

@pytest.fixture
def vector_clock():
    return VectorClock()

def test_simple_increment(vector_clock):
    vector_clock.increment()
    assert vector_clock.clock[vector_clock.node_id] == 1, "Increment failed"

def test_update_with_empty_clock(vector_clock):
    vector_clock.update({})
    assert vector_clock.clock[vector_clock.node_id] == 1, "Update with empty clock failed"

def test_update():
    vector_clock = VectorClock()
    print(vector_clock.clock)
    vector_clock.update({"1": 2, "2": 3, "3": 0})
    assert vector_clock.clock["1"] == 3, "Update failed for node1"
    assert vector_clock.clock["2"] == 3, "Update failed for node2"

def test_compare_clocks_equal(vector_clock):
    vector_clock.clock = {"1": 2, "2": 3}
    clock2 = {"1": 2, "2": 3}
    result = vector_clock.compare_clocks(clock2)
    assert result == VectorClockComparison.EQUAL, "Comparison failed for equal clocks"

def test_compare_clocks_greater(vector_clock):
    vector_clock.clock = {"1": 3, "2": 3}
    clock2 = {"1": 2, "2": 3}
    result = vector_clock.compare_clocks(clock2)
    assert result == VectorClockComparison.GREATER_THAN, "Comparison failed for greater clock"

def test_compare_clocks_less(vector_clock):
    vector_clock.clock = {"1": 2, "2": 3}
    clock2 = {"1": 3, "2": 3}
    result = vector_clock.compare_clocks(clock2)
    assert result == VectorClockComparison.LESS_THAN, "Comparison failed for less clock"

def test_compare_clocks_with_initialization():
    vc = VectorClock()
    vc.increment()
    clock = {"1": 0, "2": 0}
    result = vc.compare_clocks(clock)
    assert result == VectorClockComparison.CONCURRENT, "Concurrent comparison failed"