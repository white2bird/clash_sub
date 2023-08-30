from flask import Flask
from flask_apscheduler import APScheduler
from schedule.script.ikuuu_login import login

import logging

from util.redisUtil import Redis

logger = logging.getLogger()


def register_login_schedule(scheduler: APScheduler, app: Flask):
    @scheduler.task('cron', id='ikuuu_login', hour="10")
    def initialize_scheduler():
        with app.app_context():
            logger.info("---start  logging----")
            emails = Redis.zrevrange("emails", 0, -1)

            if emails is None or len(emails) == 0:
                return
            login(emails)
            logger.info("logging success")
