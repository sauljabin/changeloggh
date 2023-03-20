from enum import Enum


class ChangeType(Enum):
    Added = "Added"
    Changed = "Changed"
    Deprecated = "Deprecated"
    Fixed = "Fixed"
    Removed = "Removed"
    Security = "Security"
