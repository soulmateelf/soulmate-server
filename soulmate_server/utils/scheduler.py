from datetime import datetime, timedelta

from apscheduler.jobstores.redis import RedisJobStore
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.interval import IntervalTrigger
from fastapi import FastAPI
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.jobstores.base import JobLookupError, ConflictingIdError

from soulmate_server.conf.dataConf import redisConf
from soulmate_server.conf.schedulerConf import JOBS


class SchedulerManager:
    def __init__(self, redis_url='redis://default:SoulmateDev@54.177.82.194:55824/0'):
        # 创建一个RedisJobStore实例
        jobstores = {
            'redis': RedisJobStore(
                host=redisConf["host"],
                port=redisConf["port"],
                password=redisConf["password"],
                db=1
            )
        }
        self.scheduler = BackgroundScheduler(jobstores=jobstores)
        self.scheduler.start()
        # 从配置中动态加载定时任务
        for job_config in JOBS:
            job_id = job_config['id']
            job_func = job_config['func']
            job_trigger = job_config['trigger']

            try:
                self.scheduler.add_job(func=job_func, trigger=job_trigger, id=job_id)
                print(f"定时任务 '{job_id}' 添加成功")
            except Exception as e:
                print(f"添加定时任务 '{job_id}' 失败: {e}")
        print("Scheduler initialized successfully")

    def add_job(self, func, trigger, args=None):
        """
        添加定时任务
        :param func: 定时任务执行的函数
        :param trigger: 触发器
        :param args: 函数参数列表
        """
        self.scheduler.add_job(func, trigger, args=args)

    def add_single_run_job(self, func, delay_seconds, args=None):
        """
        添加只执行一次的定时任务
        :param func: 定时任务执行的函数
        :param delay_seconds: 延迟执行的时间（秒）
        :param args: 函数参数列表
        """
        # 检查是否已存在相同 lockId 的任务
        existing_jobs = self.scheduler.get_jobs()
        for existing_job in existing_jobs:
            existing_args = existing_job.args
            if existing_args and existing_args[2] == args[2]:
                print(f"任务已存在，跳过添加：lockId={args[2]}")
                return

        # 如果不存在相同 lockId 的任务，继续添加
        trigger_time = datetime.now() + timedelta(seconds=delay_seconds)
        trigger = DateTrigger(run_date=trigger_time)

        try:
            self.scheduler.add_job(func, trigger, args=args)
            print(f"定时任务添加成功：lockId={args[2]}")
        except ConflictingIdError:
            print(f"任务ID冲突，无法添加任务：lockId={args[2]}")

    def modify_job(self, job_id, trigger):
        """
        修改定时任务的触发器
        :param job_id: 定时任务的ID
        :param trigger: 新的触发器
        """
        try:
            self.scheduler.reschedule_job(job_id, trigger)
        except JobLookupError:
            print(f"Job with id {job_id} not found")

    def remove_job(self, job_id):
        """
        移除定时任务
        :param job_id: 定时任务的ID
        """
        try:
            self.scheduler.remove_job(job_id)
        except JobLookupError:
            print(f"Job with id {job_id} not found")

    def stop_scheduler(self):
        """
        停止调度器，应该在应用退出时调用
        """
        print("Stopping scheduler")
        self.scheduler.shutdown()


# 示例触发器，每隔5秒执行一次
trigger = CronTrigger(second='*/5')
