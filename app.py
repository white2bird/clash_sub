from flask import Flask, send_from_directory, request, Request
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

logger = logging.getLogger()


@app.route('/clash/sub')
def clash_sub():  # put application's code here
    random = request.args.get('random')
    user_agent = request.user_agent.string
    type_mobile = 'computer'
    if 'Mobile' in user_agent or 'Android' in user_agent or 'iPhone' in user_agent:
        type_mobile = 'mobile'
    if random is None or random != '109657':
        return {'code': 500, 'msg': 'error'}
    clash_name = "merged_clash_computer.yaml" if type_mobile != "mobile" else "merged_clash_mobile.yaml"
    return send_from_directory(app.static_folder, clash_name)


@app.route('/heart')
def heart():
    user_agent = request.user_agent.string
    if 'Mobile' in user_agent or 'Android' in user_agent or 'iPhone' in user_agent:
        logger.info("is mobile")
    else:
        logger.info("====com======")
    test_value = Redis.read("test")
    return {'status': 200, 'msg': None if test_value is None else test_value}


@app.route('/msg', methods="post")
def feishu_msg():
    logger.info("---- get request --- ")
    res = request.json.get("challenge")
    return {'status': 200, 'challenge': res}


@app.route('/getRedisUrl')
def get_redis_url():
    return {'status': 200, 'msg': app.config['SESSION_REDIS']}


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8898, debug=True)
