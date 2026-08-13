import asyncio

from app.messaging.nats_client import (
    connect_to_nats,
    subscribe_to_events,
)


async def start_notification_service():
    nc = await connect_to_nats()
    await subscribe_to_events(nc)
    print("Notification Service is running...")
    while True:
        await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(start_notification_service())