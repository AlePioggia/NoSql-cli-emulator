from enum import Enum

class VectorClockResponseState(Enum):
    ACCEPT = 0
    REJECT = 1
    NO_OP = 2