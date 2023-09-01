import time

import requests
import yaml
from bs4 import BeautifulSoup
from flask import Flask
from flask_apscheduler import APScheduler
from util.redisUtil import Redis
from schedule.script.clash_scrapy import aggregate_clash_subscriptions
import logging

logger = logging.getLogger()


def register_clash_schedule(scheduler: APScheduler, app: Flask):
    @scheduler.task('cron', id='clash_schedule', minute="*/1")
    def initialize_scheduler():
        with app.app_context():
            logger.info("---start  crawl----")
            clash_url_list = Redis.zrevrange("clash_url", 0, 1)
            if clash_url_list is None or len(clash_url_list) == 0:
                return
            static_path = app.static_folder
            url_list = [_ for _ in clash_url_list]

            clash_res_mobile = aggregate_clash_subscriptions(url_list, type_mobile="mobile")
            if clash_res_mobile and len(clash_res_mobile) > 0:
                logger.info("---clash mobile success ---------")

                with open(static_path + "/merged_clash_mobile.yaml", 'w', encoding="utf-8") as file:
                    with open(static_path + "/proxy_head.txt", 'r') as head_file:
                        lines = head_file.readlines()
                        for line in lines:
                            file.write(line)
                    yaml.dump(clash_res_mobile, file, default_flow_style=False, allow_unicode=True)

            clash_res_cp = aggregate_clash_subscriptions(url_list, type_mobile="computer")
            if clash_res_cp and len(clash_res_cp) > 0:
                logger.info("---clash computer success ---------")

                with open(static_path + "/merged_clash_computer.yaml", 'w', encoding="utf-8") as file:
                    with open(static_path + "/proxy_head.txt", 'r') as head_file:
                        lines = head_file.readlines()
                        for line in lines:
                            file.write(line)
                    yaml.dump(clash_res_cp, file, default_flow_style=False, allow_unicode=True)
            logger.info("---clash success write into yaml text---------")

    @scheduler.task('cron', id='clash_schedule_url_node_url', minute="*/2")
    def initialize_url1_scheduler():
        with app.app_context():
            nodefreeUrl = 'https://nodefree.org/'
            session = requests.session()
            res = session.get(nodefreeUrl)
            soup = BeautifulSoup(res.text, 'html.parser')
            # 使用选择器查找具有 class="item-content" 的元素
            item_content_elements = soup.select('.item-content')

            # 打印找到的元素内容
            for element in item_content_elements:
                next_url = element.a['href']
                inner_res = session.get(next_url)
                inner_soup = BeautifulSoup(inner_res.text, 'html.parser')
                section_list = inner_soup.select('.section p')
                for section in section_list:
                    if section:
                        if section.string.endswith('.yaml'):
                            Redis.zadd('clash_url', time.time(), section.string)
                            return

    @scheduler.task('cron', id='clash_schedule_clash__url', minute="*/2")
    def initial_url2_scheduler():
        with app.app_context():
            classnodeUrl = 'https://clashnode.com/'
            session = requests.session()
            res = session.get(classnodeUrl)
            soup = BeautifulSoup(res.text, 'html.parser')
            item_content_elements = soup.select('h2[cp-post-title]')

            # 打印找到的元素内容
            for element in item_content_elements:
                next_url = element.a['href']
                inner_res = session.get(next_url)

                inner_soup = BeautifulSoup(inner_res.text, 'html.parser')
                section_list = inner_soup.select('p')
                for section in section_list:
                    if section.string:
                        if section.string.endswith('.yaml'):
                            Redis.zadd('clash_url', time.time(), section.string)
                            return

                break
