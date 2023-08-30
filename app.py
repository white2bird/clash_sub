from flask import Flask, send_from_directory, request
from flask_apscheduler import APScheduler

from run import register_run, init_app, setting_log

import logging

from util.redisUtil import Redis

logging.basicConfig(filename="log.txt", level=logging.INFO)

app = Flask(__name__)
setting_log()
init_app(app)
app.app_context().push()
scheduler = APScheduler()
scheduler.init_app(app)
register_run(scheduler, app)

scheduler.start()


@app.route('/clash/sub')
def clash_sub():  # put application's code here
    random = request.args.get('random')
    if random is None or random != '1096576877':
        return {'code': 500, 'msg': 'error'}
    return send_from_directory(app.static_folder, "merged_clash.yaml")


@app.route('/heart')
def heart():
    test_value = Redis.read("test")
    return {'status': 200, 'msg': None if test_value is None else test_value}


@app.route('/getRedisUrl')
def get_redis_url():
    return {'status':200, 'msg':app.config['SESSION_REDIS']}


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8898)
