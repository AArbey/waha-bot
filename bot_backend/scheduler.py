from apscheduler.schedulers.background import BackgroundScheduler
from bot_backend.database import get_due_reminders
from datetime import datetime

def load_pending_reminders(scheduler):
    pass

def init_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.start()
    load_pending_reminders(scheduler)
    return scheduler