import os
from datetime import datetime, time
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from typing import Optional
from .database import get_active_schedulers_by_trigger, get_user_by_id
from .ai_service import ai_analyst
from .email_service import email_service
from .mcp_tools import mcp_tools
import json
import asyncio


class SchedulerService:
    """Service for managing scheduled stock alerts."""
    
    def __init__(self):
        self.scheduler: Optional[AsyncIOScheduler] = None
        self.morning_hour = 8
        self.morning_minute = 30
        self.evening_hour = 17
        self.evening_minute = 0

    def start(self):
        """Start the scheduler with morning and evening jobs."""
        if self.scheduler is None:
            self.scheduler = AsyncIOScheduler()
        
        self.scheduler.add_job(
            self._run_morning_alerts,
            CronTrigger(hour=self.morning_hour, minute=self.morning_minute),
            id="morning_alerts",
            replace_existing=True
        )
        
        self.scheduler.add_job(
            self._run_evening_alerts,
            CronTrigger(hour=self.evening_hour, minute=self.evening_minute),
            id="evening_alerts",
            replace_existing=True
        )
        
        self.scheduler.start()
        print(f"Scheduler started. Morning alerts at {self.morning_hour}:{self.morning_minute:02d}, Evening alerts at {self.evening_hour}:{self.evening_minute:02d}")

    def stop(self):
        """Stop the scheduler."""
        if self.scheduler:
            self.scheduler.shutdown()
            self.scheduler = None

    async def _run_morning_alerts(self):
        """Execute all morning scheduled alerts."""
        print(f"Running morning alerts at {datetime.now()}")
        await self._process_alerts("morning")

    async def _run_evening_alerts(self):
        """Execute all evening scheduled alerts."""
        print(f"Running evening alerts at {datetime.now()}")
        await self._process_alerts("evening")

    async def _process_alerts(self, trigger_time: str):
        """Process all active alerts for the given trigger time."""
        schedulers = get_active_schedulers_by_trigger(trigger_time)
        
        for scheduler in schedulers:
            try:
                user = get_user_by_id(scheduler["user_id"])
                if not user:
                    continue
                
                prompt = scheduler["prompt"]
                symbols = scheduler.get("symbols", [])
                
                if symbols:
                    analysis_parts = []
                    for symbol in symbols:
                        result = await ai_analyst.generate_stock_recommendation(symbol)
                        if "error" not in result:
                            analysis_parts.append(f"**{symbol}**\n{result.get('analysis', 'No analysis available')}")
                    
                    alert_content = f"Custom Prompt: {prompt}\n\n" + "\n\n---\n\n".join(analysis_parts)
                else:
                    market_summary = await ai_analyst.generate_market_summary()
                    alert_content = f"Custom Prompt: {prompt}\n\n{market_summary.get('summary', 'No summary available')}"
                
                await email_service.send_market_alert(
                    to_email=user["email"],
                    user_name=user["name"],
                    alert_content=alert_content,
                    trigger_time=trigger_time,
                    symbols=symbols
                )
                
                print(f"Alert sent to {user['email']} for scheduler {scheduler['id']}")
                
            except Exception as e:
                print(f"Error processing scheduler {scheduler['id']}: {str(e)}")

    async def run_manual_alert(self, scheduler_id: str) -> dict:
        """Manually trigger an alert for testing."""
        from .database import get_scheduler_by_id
        
        scheduler = get_scheduler_by_id(scheduler_id)
        if not scheduler:
            return {"error": "Scheduler not found"}
        
        user = get_user_by_id(scheduler["user_id"])
        if not user:
            return {"error": "User not found"}
        
        prompt = scheduler["prompt"]
        symbols = scheduler.get("symbols", [])
        
        try:
            if symbols:
                analysis_parts = []
                for symbol in symbols:
                    result = await ai_analyst.generate_stock_recommendation(symbol)
                    if "error" not in result:
                        analysis_parts.append(f"**{symbol}**\n{result.get('analysis', 'No analysis available')}")
                
                alert_content = f"Custom Prompt: {prompt}\n\n" + "\n\n---\n\n".join(analysis_parts)
            else:
                market_summary = await ai_analyst.generate_market_summary()
                alert_content = f"Custom Prompt: {prompt}\n\n{market_summary.get('summary', 'No summary available')}"
            
            email_sent = await email_service.send_market_alert(
                to_email=user["email"],
                user_name=user["name"],
                alert_content=alert_content,
                trigger_time=scheduler["trigger_time"],
                symbols=symbols
            )
            
            return {
                "success": True,
                "email_sent": email_sent,
                "content": alert_content
            }
        except Exception as e:
            return {"error": str(e)}

    def get_next_run_times(self) -> dict:
        """Get the next scheduled run times."""
        now = datetime.now()
        
        morning_time = now.replace(hour=self.morning_hour, minute=self.morning_minute, second=0, microsecond=0)
        if morning_time <= now:
            morning_time = morning_time.replace(day=morning_time.day + 1)
        
        evening_time = now.replace(hour=self.evening_hour, minute=self.evening_minute, second=0, microsecond=0)
        if evening_time <= now:
            evening_time = evening_time.replace(day=evening_time.day + 1)
        
        return {
            "morning": morning_time.isoformat(),
            "evening": evening_time.isoformat()
        }


scheduler_service = SchedulerService()
