import nats
import json
import os

NATS_URL = os.environ.get("NATS_URL", "nats://localhost:4222")


async def connect_to_nats():
    nc = await nats.connect(NATS_URL)
    print("Connected to NATS")
    return nc

async def subscribe_to_events(nc):
    async def message_handler(msg):
        data = json.loads(msg.data.decode())

        event_type = data["event_type"]
        payload = data["payload"]

        if event_type == "user.registered":

            print("Registration event received")
            print("Email:", payload["email"])
            print("Verification token:", payload["token"])
            print("Verification url:", payload["url"])

        elif event_type == "user.logged_in":

            print("\nLogin event received")
            print(f"Welcome {payload['username']}!")
            print("Email:", payload["email"])
            print("access_token:", payload["access_token"])

        elif event_type == "user.get_user":

            print("\nGet user event received")
            print(f"username: {payload['username']}!")
            print("Email:", payload["email"])



    await nc.subscribe(
        "user.registered",
        cb=message_handler
    )

    await nc.subscribe(
        "user.logged_in",
        cb=message_handler
        )
    await nc.subscribe(
        "user.get_user",
        cb=message_handler
        )
    
    print("Subscribed to user.registered")
    