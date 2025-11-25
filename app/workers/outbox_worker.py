# app/workers/outbox_worker.py
import asyncio
import json
from typing import Callable

from app.infra.db.session import AsyncSessionFactory
from app.infra.outbox.repository import OutboxRepository


async def dispatch_event(event, publisher: Callable[[str, dict], asyncio.Future]):
    """
    Publish a single outbox event using a provided publisher.
    Publisher could be a Kafka producer, Redis stream, RabbitMQ, etc.
    """
    payload = json.loads(event.payload)
    topic = f"{event.aggregate_type}.{event.event_type}"
    await publisher(topic, payload)


async def dummy_publisher(topic: str, payload: dict):
    """
    Replace this with real integration (Kafka, SNS, etc.)
    """
    print(f"[OUTBOX] Publishing to {topic}: {payload}")


async def run_outbox_loop(poll_interval: float = 2.0):
    while True:
        async with AsyncSessionFactory() as session:
            repo = OutboxRepository(session)
            events = await repo.get_unprocessed_events(limit=100)

            if not events:
                await asyncio.sleep(poll_interval)
                continue

            for ev in events:
                try:
                    await dispatch_event(ev, dummy_publisher)
                    await repo.mark_processed(ev.id)
                except Exception as e:
                    # Log and continue; leave event unprocessed for retry
                    print(f"[OUTBOX] Error processing {ev.id}: {e}")

            await session.commit()

        await asyncio.sleep(poll_interval)


if __name__ == "__main__":
    asyncio.run(run_outbox_loop())
