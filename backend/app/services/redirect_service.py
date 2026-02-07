import json
import hashlib
from datetime import datetime
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.core.database import AsyncSessionLocal
from app.core.redis_client import redis_client
from app.models import TrackingLink, AnalyticsEvent, Campaign, User
import logging

logger = logging.getLogger(__name__)

class RedirectService:
    @staticmethod
    async def get_target_url(short_code: str) -> str | None:
        """Get the target URL for a tracking link."""
        # 1. Try Cache
        cached_url = await redis_client.get(f"link:{short_code}")
        if cached_url:
            return cached_url

        # 2. DB Lookup with campaign join
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(TrackingLink)
                .options(
                    selectinload(TrackingLink.campaign),
                    selectinload(TrackingLink.target)  # For backward compatibility
                )
                .where(TrackingLink.short_code == short_code)
            )
            link = result.scalars().first()
            
            if not link:
                return None
            
            # Get target URL from campaign or target
            if link.campaign and link.campaign.target_url:
                target_url = link.campaign.target_url
            elif link.target and link.target.target_value:
                target_url = link.target.target_value
            else:
                return None
            
            # Cache it (TTL 24 hours)
            await redis_client.set(f"link:{short_code}", target_url, ex=86400)
            return target_url

    @staticmethod
    def _generate_visitor_hash(metadata: dict) -> str:
        """Generate a unique hash for a visitor based on IP + User Agent."""
        identifier = f"{metadata.get('ip', '')}_{metadata.get('user_agent', '')}"
        return hashlib.md5(identifier.encode()).hexdigest()[:16]

    @staticmethod
    async def log_click(short_code: str, metadata: dict):
        """
        Background task to log the click and award agents for unique views.
        """
        try:
            async with AsyncSessionLocal() as session:
                # Get the tracking link with related data
                result = await session.execute(
                    select(TrackingLink)
                    .options(selectinload(TrackingLink.campaign))
                    .where(TrackingLink.short_code == short_code)
                )
                link = result.scalars().first()
                if not link:
                    return

                # Always increment total view count
                link.view_count = (link.view_count or 0) + 1
                
                # Check if this is a unique view
                visitor_hash = RedirectService._generate_visitor_hash(metadata)
                unique_key = f"unique:{short_code}:{visitor_hash}"
                
                is_unique = await redis_client.get(unique_key) is None
                
                if is_unique:
                    # Mark as seen (expire after 30 days)
                    await redis_client.set(unique_key, "1", ex=2592000)
                    
                    # Increment unique view count
                    link.unique_view_count = (link.unique_view_count or 0) + 1
                    
                    # Award the agent if campaign exists
                    if link.campaign and link.agent_id:
                        campaign = link.campaign
                        
                        # Check budget
                        current_spent = campaign.spent or 0
                        payout = campaign.payout_per_view or 0
                        
                        if current_spent + payout <= campaign.budget_cap:
                            # Update campaign stats
                            campaign.spent = current_spent + payout
                            campaign.total_unique_views = (campaign.total_unique_views or 0) + 1
                            
                            # Award the agent
                            agent_result = await session.execute(
                                select(User).where(User.id == link.agent_id)
                            )
                            agent = agent_result.scalars().first()
                            
                            if agent:
                                # Add money
                                agent.wallet_balance = (agent.wallet_balance or 0) + payout
                                
                                # Add points
                                points = campaign.points_per_view or 1
                                agent.current_score = (agent.current_score or 0) + points
                                
                                logger.info(
                                    f"Awarded agent {agent.id}: +${payout:.2f}, +{points} pts "
                                    f"for campaign {campaign.name}"
                                )
                    
                    # Log as unique event
                    event_type = "UNIQUE_VIEW"
                else:
                    event_type = "VIEW"
                
                # Update campaign total views
                if link.campaign:
                    link.campaign.total_views = (link.campaign.total_views or 0) + 1
                
                # Create analytics event
                event = AnalyticsEvent(
                    event_type=event_type,
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
