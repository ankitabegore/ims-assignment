from abc import ABC, abstractmethod
from models.work_item import WorkItem
import logging

logger = logging.getLogger(__name__)

class AlertStrategy(ABC):
    @abstractmethod
    def send_alert(self, work_item: WorkItem):
        pass

class P0Strategy(AlertStrategy):
    def send_alert(self, work_item: WorkItem):
        logger.critical(f"P0 ALERT! Component {work_item.component_id} is down! Paging on-call...")

class P1Strategy(AlertStrategy):
    def send_alert(self, work_item: WorkItem):
        logger.error(f"P1 ALERT! Component {work_item.component_id} requires immediate attention.")

class P2Strategy(AlertStrategy):
    def send_alert(self, work_item: WorkItem):
        logger.warning(f"P2 ALERT! Component {work_item.component_id} degraded. Please investigate.")

class P3Strategy(AlertStrategy):
    def send_alert(self, work_item: WorkItem):
        logger.info(f"P3 ALERT! Minor issue on component {work_item.component_id}. Logged for triage.")

def get_alert_strategy(priority) -> AlertStrategy:
    from models.enums import Priority
    strategies = {
        Priority.P0: P0Strategy(),
        Priority.P1: P1Strategy(),
        Priority.P2: P2Strategy(),
        Priority.P3: P3Strategy(),
    }
    return strategies.get(priority, P3Strategy())
