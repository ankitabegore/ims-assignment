import pytest
from models.work_item import WorkItem, RCA
from models.enums import Status, RootCauseCategory
from workflow.state_machine import get_state_machine, InvalidTransitionError, RCAMissingError

def test_rca_validation_on_close():
    wi = WorkItem(id="1", component_id="db", title="test", status=Status.RESOLVED)
    sm = get_state_machine(wi)
    
    # Attempting to close without RCA should raise RCAMissingError
    with pytest.raises(RCAMissingError):
        sm.transition(Status.CLOSED)
        
    # Now add RCA and it should succeed
    wi.rca = RCA(category=RootCauseCategory.HARDWARE, description="Disk failed", preventative_actions=["Replace disk"])
    new_state = sm.transition(Status.CLOSED)
    
    assert wi.status == Status.CLOSED
    assert new_state.__class__.__name__ == "ClosedState"

def test_invalid_transitions():
    wi = WorkItem(id="2", component_id="db", title="test", status=Status.OPEN)
    sm = get_state_machine(wi)
    
    # OPEN -> CLOSED directly is invalid
    with pytest.raises(InvalidTransitionError):
        sm.transition(Status.CLOSED)
