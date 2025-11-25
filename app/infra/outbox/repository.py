# app/infra/outbox/repository.py
import json
from datetime import datetime
from typing import List

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.infra.outbox.models import OutboxEvent


class OutboxRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_event(
        self,
        aggregate_type: str,
        aggregate_id: str,
        event_type: str,
        payload: dict,
    ):
        event = OutboxEvent(
            aggregate_type=aggregate_type,
            aggregate_id=aggregate_id,
            event_type=event_type,
            payload=json.dumps(payload),
        )
        self.session.add(event)

    async def get_unprocessed_events(self, limit: int = 100) -> List[OutboxEvent]:
        stmt = (
            select(OutboxEvent)
            .where(OutboxEvent.processed == False)  # noqa: E712
            .order_by(OutboxEvent.created_at)
            .limit(limit)
        )
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    async def mark_processed(self, event_id: str):
        stmt = (
            update(OutboxEvent)
            .where(OutboxEvent.id == event_id)
            .values(processed=True, processed_at=datetime.utcnow())
        )
        await self.session.execute(stmt)
