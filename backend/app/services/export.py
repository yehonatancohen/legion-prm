"""
Export Service

Generates text reports and exports for managers.
Includes agent status, progress tracking, and inactivity alerts.
"""

import uuid
from datetime import datetime, timedelta
from typing import List, Optional
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.tenant import User, UserRole
from app.models.contacts import VcfBatch, VcfBatchStatus, AgentProgress


class ExportService:
    """Service for generating manager reports and exports."""
    
    async def get_agent_status_list(
        self,
        session: AsyncSession,
        tenant_id: uuid.UUID
    ) -> List[dict]:
        """
        Get status of all agents for a tenant.
        Includes activity status and progress.
        """
        # Get all agents for tenant
        result = await session.execute(
            select(User)
            .where(User.tenant_id == tenant_id)
            .where(User.role == UserRole.AGENT.value)
            .order_by(User.name)
        )
        agents = result.scalars().all()
        
        now = datetime.utcnow()
        agent_statuses = []
        
        for agent in agents:
            # Calculate inactivity
            last_activity = agent.last_activity_at or agent.created_at
            inactive_days = (now - last_activity).days
            
            # Get today's progress
            today = datetime.utcnow().date()
            progress_result = await session.execute(
                select(AgentProgress)
                .where(AgentProgress.agent_id == agent.id)
                .where(AgentProgress.date == today)
            )
            today_progress = progress_result.scalars().first()
            
            # Get total progress
            total_result = await session.execute(
                select(
                    func.sum(AgentProgress.morning_count + AgentProgress.evening_count)
                )
                .where(AgentProgress.agent_id == agent.id)
            )
            total_added = total_result.scalar() or 0
            
            # Get assigned batch info
            batch_result = await session.execute(
                select(VcfBatch)
                .where(VcfBatch.agent_id == agent.id)
                .where(VcfBatch.status.in_([
                    VcfBatchStatus.ASSIGNED.value,
                    VcfBatchStatus.IN_PROGRESS.value
                ]))
            )
            active_batch = batch_result.scalars().first()
            
            # Determine status
            if inactive_days >= 5:
                status = "INACTIVE"
                status_icon = "❌"
            elif inactive_days >= 1:
                status = "WARNING"
                status_icon = "⚠️"
            else:
                status = "ACTIVE"
                status_icon = "✅"
            
            agent_statuses.append({
                "id": str(agent.id),
                "name": agent.name,
                "phone": agent.phone,
                "status": status,
                "status_icon": status_icon,
                "inactive_days": inactive_days,
                "last_activity": last_activity.isoformat() if last_activity else None,
                "today_morning": today_progress.morning_count if today_progress else 0,
                "today_evening": today_progress.evening_count if today_progress else 0,
                "today_total": (
                    (today_progress.morning_count if today_progress else 0) +
                    (today_progress.evening_count if today_progress else 0)
                ),
                "total_added": total_added,
                "has_active_batch": active_batch is not None,
                "batch_contacts": active_batch.contact_count if active_batch else 0,
                "tutorial_completed": agent.tutorial_completed
            })
        
        return agent_statuses
    
    async def get_inactive_agents(
        self,
        session: AsyncSession,
        tenant_id: uuid.UUID,
        inactive_threshold_days: int = 1
    ) -> List[dict]:
        """Get agents who haven't been active for specified days."""
        all_agents = await self.get_agent_status_list(session, tenant_id)
        return [a for a in all_agents if a["inactive_days"] >= inactive_threshold_days]
    
    async def generate_text_report(
        self,
        session: AsyncSession,
        tenant_id: uuid.UUID
    ) -> str:
        """
        Generate a text status report for managers.
        Can be copied and shared via WhatsApp/email.
        """
        agent_statuses = await self.get_agent_status_list(session, tenant_id)
        
        # Calculate summary stats
        total_agents = len(agent_statuses)
        active_today = sum(1 for a in agent_statuses if a["today_total"] > 0)
        inactive_count = sum(1 for a in agent_statuses if a["status"] == "INACTIVE")
        warning_count = sum(1 for a in agent_statuses if a["status"] == "WARNING")
        
        total_today = sum(a["today_total"] for a in agent_statuses)
        total_all_time = sum(a["total_added"] for a in agent_statuses)
        
        # Build report
        now = datetime.utcnow()
        report_lines = [
            "=== LEGION PRM STATUS REPORT ===",
            f"Generated: {now.strftime('%Y-%m-%d %H:%M')} UTC",
            "",
            "SUMMARY",
            "-------",
            f"Total Agents: {total_agents}",
            f"Active Today: {active_today}",
            f"Inactive (>1 day): {warning_count + inactive_count}",
            f"Contacts Added Today: {total_today}",
            f"Total Contacts Added: {total_all_time}",
            "",
            "AGENT DETAILS",
            "-------------"
        ]
        
        # Sort: active first, then warning, then inactive
        status_order = {"ACTIVE": 0, "WARNING": 1, "INACTIVE": 2}
        sorted_agents = sorted(agent_statuses, key=lambda a: status_order.get(a["status"], 3))
        
        for agent in sorted_agents:
            # Format line
            name_padded = agent["name"][:15].ljust(15)
            today_str = f"Today: {agent['today_total']}/50"
            total_str = f"Total: {agent['total_added']:,}"
            
            if agent["status"] == "ACTIVE":
                line = f"{agent['status_icon']} {name_padded} | {today_str} | {total_str}"
            elif agent["status"] == "WARNING":
                line = f"{agent['status_icon']} {name_padded} | {today_str} | Last Active: {agent['inactive_days']} day(s) ago"
            else:
                line = f"{agent['status_icon']} {name_padded} | INACTIVE     | Last Active: {agent['inactive_days']} days ago"
            
            report_lines.append(line)
        
        return "\n".join(report_lines)
    
    async def get_daily_summary(
        self,
        session: AsyncSession,
        tenant_id: uuid.UUID,
        date: Optional[datetime] = None
    ) -> dict:
        """Get summary statistics for a specific date."""
        if date is None:
            date = datetime.utcnow().date()
        
        # Get progress for the date
        result = await session.execute(
            select(AgentProgress)
            .join(User)
            .where(User.tenant_id == tenant_id)
            .where(AgentProgress.date == date)
        )
        progress_records = result.scalars().all()
        
        total_morning = sum(p.morning_count for p in progress_records)
        total_evening = sum(p.evening_count for p in progress_records)
        agents_reported = len(progress_records)
        
        return {
            "date": date.isoformat(),
            "agents_reported": agents_reported,
            "morning_total": total_morning,
            "evening_total": total_evening,
            "day_total": total_morning + total_evening
        }


# Singleton instance
export_service = ExportService()
