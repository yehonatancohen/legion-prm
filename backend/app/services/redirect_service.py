import json
from datetime import datetime
from sqlalchemy.future import select
from app.core.database import AsyncSessionLocal
from app.core.redis_client import redis_client
from app.models import TrackingLink, AnalyticsEvent
import logging

logger = logging.getLogger(__name__)

class RedirectService:
    @staticmethod
    async def get_target_url(short_code: str) -> str | None:
        # 1. Try Cache
        cached_url = await redis_client.get(f"link:{short_code}")
        if cached_url:
            return cached_url

        # 2. DB Lookup
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(TrackingLink).where(TrackingLink.short_code == short_code))
            link = result.scalars().first()
            
            if link:
                # 3. Cache it (TTL 24 hours)
                target_url = link.target.target_value
                # We need to load target eagerly or join, but for now assuming lazy load works if attached, 
                # actually in async we need explicit join or selectinload options usually.
                # Let's do a join to be safe.
                # But wait, scalar access to relation might trigger IO error in async if not loaded.
                # let's fix the query below.
                pass
            else:
                return None

        # Re-query with join if needed or simple optimization:
        # Storing target_url in TrackingLink would be faster but normalization is cleaner.
        # Let's do a joined load query.
        async with AsyncSessionLocal() as session:
            from sqlalchemy.orm import selectinload
            result = await session.execute(
                select(TrackingLink)
                .options(selectinload(TrackingLink.target))
                .where(TrackingLink.short_code == short_code)
            )
            link = result.scalars().first()
            if not link or not link.target:
                return None
            
            target_url = link.target.target_value
            await redis_client.set(f"link:{short_code}", target_url, ex=86400)
            return target_url

    @staticmethod
    async def log_click(short_code: str, metadata: dict):
        """
        Background task to log the click.
        """
        try:
            async with AsyncSessionLocal() as session:
                # We need to know who the agent is to log it properly in events?
                # The TrackingLink has agent_id. We might want to cache agent_id too if we want to avoid DB read here.
                # For now, let's read from DB.
                result = await session.execute(select(TrackingLink).where(TrackingLink.short_code == short_code))
                link = result.scalars().first()
                if not link:
                    return

                event = AnalyticsEvent(
                    event_type="CLICK",
                    tracking_link_id=short_code,
                    agent_id=link.agent_id,
                    metadata_json=json.dumps(metadata)
                )
                session.add(event)
                await session.commit()
                
                # Optional: Increment realtime counter in Redis
                await redis_client.incr(f"stats:link:{short_code}:clicks")
                if link.agent_id:
                     await redis_client.incr(f"stats:agent:{link.agent_id}:clicks")

        except Exception as e:
            logger.error(f"Error logging click for {short_code}: {e}")
