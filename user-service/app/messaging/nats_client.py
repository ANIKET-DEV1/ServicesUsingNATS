import nats
import json
from ..schemas.event import EventEnvelope

NATS_URL = "nats://localhost:4222"


async def connect_to_nats():
    nc = await nats.connect(NATS_URL)
    print("User Service connected to NATS")
    return nc


async def publish_event(
    nc,
    subject: str,
    event: EventEnvelope,
):
    await nc.publish(
        event.model_dump_json().encode()
    )

    await nc.flush()

    print(f"Published event: {subject}")