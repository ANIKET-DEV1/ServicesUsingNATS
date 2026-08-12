import nats
import json

NATS_URL = "nats://localhost:4222"


async def connect_to_nats():
    nc = await nats.connect(NATS_URL)
    print("User Service connected to NATS")
    return nc



async def publish_user_registered(nc, user_id: str, email: str):

    event = {
        "event_type": "user.registered",
        "user_id": user_id,
        "email": email,
    }

    await nc.publish(
        "user.registered",
        json.dumps(event).encode()
    )

    await nc.flush()

    print("Published user.registered event")