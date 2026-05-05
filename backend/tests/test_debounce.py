import pytest
import asyncio
from queue.debounce import Debouncer
from models.signal import Signal

@pytest.mark.asyncio
async def test_debounce_window():
    results = []
    async def mock_callback(comp_id, signals):
        results.append((comp_id, signals))
        
    # fast debouncer for test
    debouncer = Debouncer(window_seconds=1, callback=mock_callback)
    
    s1 = Signal(id="1", component_id="db", message="timeout")
    s2 = Signal(id="2", component_id="db", message="timeout again")
    s3 = Signal(id="3", component_id="api", message="timeout")
    
    await debouncer.add_signal(s1)
    await debouncer.add_signal(s2)
    await debouncer.add_signal(s3)
    
    # Should not be processed yet
    assert len(results) == 0
    
    # Wait for window to close
    await asyncio.sleep(1.2)
    
    # Both 'db' and 'api' should have been processed
    assert len(results) == 2
    
    # Check that 'db' grouped s1 and s2
    db_group = next(r[1] for r in results if r[0] == "db")
    assert len(db_group) == 2
    assert db_group[0].id == "1"
    assert db_group[1].id == "2"
