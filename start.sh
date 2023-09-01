#!/bin/bash

nohup gunicorn -w 1 -b 0.0.0.0:8898 app:app &> /root/python/work/flask_clash/flask_clash/logs/clash.log &

#nohup gunicorn -w 1 -b 0.0.0.0:8898 app:app &> ./logs/clash.log &