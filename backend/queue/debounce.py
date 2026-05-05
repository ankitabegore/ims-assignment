import asyncio
from typing import List, Dict
from models.signal import Signal

class Debouncer:
    def __init__(self, window_seconds: int = 10, callback=None):
        self.window_seconds = window_seconds
        self.callback = callback
        self.buffers: Dict[str, List[Signal]] = {}
        self.locks: Dict[str, asyncio.Lock] = {}

    async def add_signal(self, signal: Signal):
        comp_id = signal.component_id
        
        if comp_id not in self.locks:
            self.locks[comp_id] = asyncio.Lock()
            
        async with self.locks[comp_id]:
            if comp_id not in self.buffers:
                self.buffers[comp_id] = [signal]
                # Start window timer
                asyncio.create_task(self._process_window(comp_id))
            else:
                self.buffers[comp_id].append(signal)

    async def _process_window(self, comp_id: str):
        await asyncio.sleep(self.window_seconds)
        
        async with self.locks[comp_id]:
            signals_to_process = self.buffers.pop(comp_id, [])
            
        if self.callback and signals_to_process:
            # We fire the callback asynchronously so we don't hold the lock
            asyncio.create_task(self.callback(comp_id, signals_to_process))

debouncer = Debouncer(window_seconds=10)
