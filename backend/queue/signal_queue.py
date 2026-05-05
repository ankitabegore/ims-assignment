import asyncio

# Global queue for backpressure buffer
# Size 10000 ensures we can absorb a large spike without crashing or dropping
signal_queue = asyncio.Queue(maxsize=10000)
