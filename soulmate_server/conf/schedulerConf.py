# config.py

from apscheduler.triggers.cron import CronTrigger

from soulmate_server.utils.schedulerTask import my_job, intimacy_job, createCircleOfFriends

# 定时任务配置
JOBS = [
    {
        'id': 'intimacy_job',
        'func': intimacy_job,
        'trigger': CronTrigger(second=0, minute=0, hour=0),
    },
    {
        'id': 'createRoleMemory_job',
        'func': createCircleOfFriends,
        'trigger': CronTrigger(second=1, minute=1, hour=11),
    }
]
