from enum import Enum
from typing import Dict

class VectorClockComparison(Enum):
    EQUAL = 0
    LESS_THAN = 1
    GREATER_THAN = 2
    CONCURRENT = 3