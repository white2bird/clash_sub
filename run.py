import os
from logging.handlers import TimedRotatingFileHandler

from flask import Flask
from flask_apscheduler import APScheduler

from schedule.ikuuu_login_schedule import register_login_schedule
from schedule.clash_scrapy_schedule import register_clash_schedule
import logging


def register_run(scheduler: APScheduler, app: Flask):
    register_login_schedule(scheduler, app)
    register_clash_schedule(scheduler, app)


def init_app(app: Flask):
    redis_url = os.environ.get("redis_url", "redis://localhost:6379")
    app.config['SESSION_TYPE'] = 'redis'
    app.config['SESSION_REDIS'] = redis_url
    app.config['REDIS_HOST'] = '127.0.0.1'
    app.config['REDIS_PORT'] = '6379'
    app.config['REDIS_DB'] = '0'


def setting_log():
    if not os.path.exists('./logs'):
        os.makedirs('./logs')
    logging.basicConfig(level=logging.INFO)
    # 每天归档 保留最近7天的数据
    file_handler = TimedRotatingFileHandler("./logs/app.log", when="midnight", interval=1, backupCount=7)
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))

    # 将文件日志处理器添加到根日志记录器
    logging.getLogger('').addHandler(file_handler)

    # 控制台的日志
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    # 创建日志格式
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    # 将处理程序添加到应用程序日志
    logging.getLogger('').addHandler(console_handler)
