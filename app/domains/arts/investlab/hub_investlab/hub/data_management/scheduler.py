"""
Scheduler - Manages automated data fetching and processing
"""

import asyncio
import logging
import schedule
import time
from datetime import datetime
from typing import Callable
import threading

logger = logging.getLogger(__name__)

class DataScheduler:
    """Manages scheduled data fetching and processing"""
    
    def __init__(self, data_hub):
        self.data_hub = data_hub
        self.is_running = False
        self.scheduler_thread = None
        self.job_count = 0
        
    def schedule_hourly_fetch(self):
        """Schedule data fetching every hour"""
        schedule.every().hour.do(self._run_async_fetch)
        logger.info("Scheduled hourly data fetching")
    
    def schedule_daily_fetch(self, time_str: str = "09:00"):
        """Schedule daily data fetching at specified time"""
        schedule.every().day.at(time_str).do(self._run_async_fetch)
        logger.info(f"Scheduled daily data fetching at {time_str}")
    
    def schedule_custom_interval(self, interval_minutes: int):
        """Schedule data fetching at custom intervals"""
        schedule.every(interval_minutes).minutes.do(self._run_async_fetch)
        logger.info(f"Scheduled data fetching every {interval_minutes} minutes")
    
    def _run_async_fetch(self):
        """Run async fetch in a separate thread"""
        def run_fetch():
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(self.data_hub.fetch_all_ecosystems())
                loop.close()
                self.job_count += 1
                logger.info(f"Scheduled fetch completed. Total jobs: {self.job_count}")
            except Exception as e:
                logger.error(f"Error in scheduled fetch: {str(e)}")
        
        # Run in separate thread to avoid blocking
        thread = threading.Thread(target=run_fetch)
        thread.start()
        return schedule.CancelJob  # Run once per schedule
    
    def start_scheduler(self):
        """Start the scheduler in a separate thread"""
        if self.is_running:
            logger.warning("Scheduler is already running")
            return
        
        self.is_running = True
        self.scheduler_thread = threading.Thread(target=self._run_scheduler)
        self.scheduler_thread.daemon = True
        self.scheduler_thread.start()
        logger.info("Data scheduler started")
    
    def _run_scheduler(self):
        """Main scheduler loop"""
        while self.is_running:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    
    def stop_scheduler(self):
        """Stop the scheduler"""
        self.is_running = False
        schedule.clear()
        logger.info("Data scheduler stopped")
    
    def get_scheduler_status(self) -> dict:
        """Get current scheduler status"""
        return {
            'is_running': self.is_running,
            'job_count': self.job_count,
            'next_runs': [
                {
                    'job': str(job),
                    'next_run': job.next_run.strftime('%Y-%m-%d %H:%M:%S') if job.next_run else None
                }
                for job in schedule.get_jobs()
            ]
        }
    
    def add_custom_job(self, job_func: Callable, interval_type: str, **kwargs):
        """Add a custom scheduled job"""
        if interval_type == 'minutes':
            minutes = kwargs.get('minutes', 60)
            schedule.every(minutes).minutes.do(job_func)
        elif interval_type == 'hours':
            hours = kwargs.get('hours', 1)
            schedule.every(hours).hours.do(job_func)
        elif interval_type == 'days':
            time_str = kwargs.get('time', '09:00')
            schedule.every().day.at(time_str).do(job_func)
        elif interval_type == 'weeks':
            day = kwargs.get('day', 'monday')
            time_str = kwargs.get('time', '09:00')
            getattr(schedule.every(), day).at(time_str).do(job_func)
        
        logger.info(f"Added custom job: {job_func.__name__} with {interval_type} interval")
