from enum import Enum

class Priority(str, Enum):
    P0 = "P0"
    P1 = "P1"
    P2 = "P2"
    P3 = "P3"

class Status(str, Enum):
    OPEN = "OPEN"
    INVESTIGATING = "INVESTIGATING"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"

class RootCauseCategory(str, Enum):
    HARDWARE = "HARDWARE"
    SOFTWARE = "SOFTWARE"
    NETWORK = "NETWORK"
    HUMAN_ERROR = "HUMAN_ERROR"
    UNKNOWN = "UNKNOWN"
