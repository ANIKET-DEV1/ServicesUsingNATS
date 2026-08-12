import nats

NATS_URL = "nats://localhost:4222"


async def connect_to_nats():
    nc = await nats.connect(NATS_URL)
    print("Connected to NATS")
    return nc


async def subscribe_to_events(nc):

    async def message_handler(msg):
        print("Message received!")
        print("Subject:", msg.subject)
        print("Data:", msg.data.decode())

    await nc.subscribe(
        "user.registered",
        cb=message_handler
    )

    print("Subscribed to user.registered")