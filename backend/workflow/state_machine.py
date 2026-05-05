from abc import ABC, abstractmethod
from models.enums import Status
from models.work_item import WorkItem

class InvalidTransitionError(Exception):
    pass

class RCAMissingError(Exception):
    pass

class WorkItemState(ABC):
    def __init__(self, work_item: WorkItem):
        self.work_item = work_item

    @abstractmethod
    def transition(self, new_status: Status) -> 'WorkItemState':
        pass

class OpenState(WorkItemState):
    def transition(self, new_status: Status) -> WorkItemState:
        if new_status == Status.INVESTIGATING:
            self.work_item.status = Status.INVESTIGATING
            return InvestigatingState(self.work_item)
        elif new_status == Status.RESOLVED:
            self.work_item.status = Status.RESOLVED
            return ResolvedState(self.work_item)
        raise InvalidTransitionError(f"Cannot transition from OPEN to {new_status}")

class InvestigatingState(WorkItemState):
    def transition(self, new_status: Status) -> WorkItemState:
        if new_status == Status.RESOLVED:
            self.work_item.status = Status.RESOLVED
            return ResolvedState(self.work_item)
        elif new_status == Status.OPEN:
            self.work_item.status = Status.OPEN
            return OpenState(self.work_item)
        raise InvalidTransitionError(f"Cannot transition from INVESTIGATING to {new_status}")

class ResolvedState(WorkItemState):
    def transition(self, new_status: Status) -> WorkItemState:
        if new_status == Status.CLOSED:
            if not self.work_item.rca:
                raise RCAMissingError("Cannot close incident without a complete RCA object.")
            self.work_item.status = Status.CLOSED
            return ClosedState(self.work_item)
        elif new_status == Status.INVESTIGATING:
            self.work_item.status = Status.INVESTIGATING
            return InvestigatingState(self.work_item)
        raise InvalidTransitionError(f"Cannot transition from RESOLVED to {new_status}")

class ClosedState(WorkItemState):
    def transition(self, new_status: Status) -> WorkItemState:
        raise InvalidTransitionError("Cannot transition from CLOSED state.")

def get_state_machine(work_item: WorkItem) -> WorkItemState:
    if work_item.status == Status.OPEN:
        return OpenState(work_item)
    elif work_item.status == Status.INVESTIGATING:
        return InvestigatingState(work_item)
    elif work_item.status == Status.RESOLVED:
        return ResolvedState(work_item)
    elif work_item.status == Status.CLOSED:
        return ClosedState(work_item)
    raise ValueError(f"Unknown status {work_item.status}")
