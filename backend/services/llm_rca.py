import random
from models.enums import RootCauseCategory

async def generate_mock_rca(component_id: str):
    reasons = [
        "A bad deployment caused a memory leak.",
        "Database connection pool exhausted due to spike in traffic.",
        "Network partition between availability zones.",
        "A misconfigured firewall rule blocked internal traffic."
    ]
    actions = [
        "Implement stricter deployment gates.",
        "Increase database connection pool limits.",
        "Add automated tests for firewall rules.",
        "Improve network failover mechanisms."
    ]
    
    reason = random.choice(reasons)
    
    category = RootCauseCategory.UNKNOWN
    if "deployment" in reason:
        category = RootCauseCategory.SOFTWARE
    elif "network" in reason.lower() or "firewall" in reason.lower():
        category = RootCauseCategory.NETWORK
        
    return {
        "category": category,
        "description": f"AI Suggester Analysis: Based on the signal patterns for {component_id}, it appears that {reason}",
        "preventative_actions": [random.choice(actions)]
    }
