import asyncio

class NATSClient:
    async def connect(self, url: str):
        await asyncio.sleep(0.01)

    async def subscribe(self, subject: str, cb):
        # Placeholder: in real code, register subscriber
        await asyncio.sleep(0.01)


nats_client = NATSClient()
