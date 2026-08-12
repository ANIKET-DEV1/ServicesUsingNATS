import nats
import json

NATS_URL = "nats://localhost:4222"


async def connect_to_nats():
    nc = await nats.connect(NATS_URL)
    print("Connected to NATS")
    return nc

async def subscribe_to_events(nc):
    async def message_handler(msg):
        data = json.loads(msg.data.decode())
        print("Event received")
        print("Event type:", data["event_type"])

        payload = data["payload"]
        print("Email:", payload["email"])
        print("Verification token:", payload["token"])
        print("Verification url:", payload["url"])

    await nc.subscribe(
        "user.registered",
        cb=message_handler
    )

    print("Subscribed to user.registered")
    