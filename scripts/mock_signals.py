import asyncio
import httpx
import uuid
import time
import random

API_URL = "http://localhost:8000/signals"

async def send_signal(client, component_id):
    signal = {
        "id": str(uuid.uuid4()),
        "component_id": component_id,
        "message": f"Connection timeout or failure in {component_id}",
    }
    try:
        response = await client.post(API_URL, json=signal)
        return response.status_code
    except Exception as e:
        return 503

async def main():
    print("Starting simulated RDBMS cascade failure...")
    
    components = [
        "auth-db-primary",
        "user-service",
        "billing-service",
        "payment-gateway"
    ]
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        tasks = []
        # Simulate a burst of 1000 signals to trigger debouncing and backpressure
        for i in range(1000):
            # 80% of failures are root cause auth-db
            comp = "auth-db-primary" if random.random() < 0.8 else random.choice(components[1:])
            tasks.append(send_signal(client, comp))
            
        results = await asyncio.gather(*tasks)
        
        success = sum(1 for r in results if r == 202)
        rate_limited = sum(1 for r in results if r == 429)
        dropped = sum(1 for r in results if r == 503)
        
        print(f"Sent 1000 signals:")
        print(f"Accepted (202): {success}")
        print(f"Rate Limited (429): {rate_limited}")
        print(f"Queue Full/Error (503): {dropped}")

if __name__ == "__main__":
    asyncio.run(main())
