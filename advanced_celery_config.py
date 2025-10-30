"""
Enhanced Celery Configuration for Chunker_v2
Advanced task management without Airflow complexity
"""

import os
import logging
from celery import Celery
from celery.schedules import crontab
from kombu import Queue

logger = logging.getLogger(__name__)

# Advanced Celery Configuration
ADVANCED_CELERY_CONFIG = {
    # Broker and Backend
    'broker_url': os.getenv('REDIS_URL', 'redis://localhost:6379/0'),
    'result_backend': os.getenv('REDIS_URL', 'redis://localhost:6379/0'),
    
    # Serialization
    'task_serializer': 'json',
    'accept_content': ['json'],
    'result_serializer': 'json',
    'timezone': 'UTC',
    'enable_utc': True,
    
    # Task Execution
    'task_track_started': True,
    'task_time_limit': 300,  # 5 minutes
    'task_soft_time_limit': 240,  # 4 minutes
    'task_acks_late': True,
    'worker_prefetch_multiplier': 1,
    'worker_disable_rate_limits': True,
    
    # Task Routing
    'task_routes': {
        'celery_tasks.process_file_task': {'queue': 'file_processing'},
        'celery_tasks.batch_process_files_task': {'queue': 'batch_processing'},
        'celery_tasks.evaluate_rag_task': {'queue': 'evaluation'},
    },
    
    # Queue Configuration
    'task_default_queue': 'default',
    'task_queues': (
        Queue('default', routing_key='default'),
        Queue('file_processing', routing_key='file_processing'),
        Queue('batch_processing', routing_key='batch_processing'),
        Queue('evaluation', routing_key='evaluation'),
        Queue('priority', routing_key='priority'),
    ),
    
    # Periodic Tasks (replaces Airflow scheduling)
    'beat_schedule': {
        'daily-evaluation': {
            'task': 'celery_tasks.run_daily_evaluation',
            'schedule': crontab(hour=2, minute=0),  # 2 AM daily
        },
        'weekly-cleanup': {
            'task': 'celery_tasks.cleanup_old_chunks',
            'schedule': crontab(hour=3, minute=0, day_of_week=1),  # Monday 3 AM
        },
        'hourly-health-check': {
            'task': 'celery_tasks.health_check',
            'schedule': crontab(minute=0),  # Every hour
        },
    },
    
    # Error Handling
    'task_annotations': {
        'celery_tasks.process_file_task': {'rate_limit': '10/m'},
        'celery_tasks.batch_process_files_task': {'rate_limit': '5/m'},
    },
    
    # Monitoring
    'worker_send_task_events': True,
    'task_send_sent_event': True,
}

class AdvancedCeleryManager:
    """
    Advanced Celery management without Airflow complexity.
    """
    
    def __init__(self, config: dict):
        self.config = config
        self.app = Celery('chunker_v2_advanced')
        self.app.config_from_object(ADVANCED_CELERY_CONFIG)
        
    def start_worker(self, queue: str = 'default', concurrency: int = 4):
        """Start Celery worker for specific queue."""
        self.app.worker_main([
            'worker',
            f'--queues={queue}',
            f'--concurrency={concurrency}',
            '--loglevel=info'
        ])
    
    def start_beat_scheduler(self):
        """Start Celery beat scheduler for periodic tasks."""
        self.app.control.start_beat()
    
    def monitor_tasks(self):
        """Monitor active tasks."""
        active = self.app.control.inspect().active()
        return active
    
    def get_queue_lengths(self):
        """Get queue lengths."""
        inspect = self.app.control.inspect()
        return {
            'active': inspect.active(),
            'scheduled': inspect.scheduled(),
            'reserved': inspect.reserved()
        }

# Usage example
if __name__ == "__main__":
    manager = AdvancedCeleryManager({})
    print("Advanced Celery configuration ready!")
    print("Start workers with: python -m celery worker -A celery_tasks -Q file_processing")
    print("Start beat with: python -m celery beat -A celery_tasks")
