from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.job import Job

scheduler: BackgroundScheduler = BackgroundScheduler()
