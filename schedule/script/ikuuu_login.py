import requests, json
import re
from datetime import datetime
import hmac
import hashlib
import base64
from requests import Session
import logging

logger = logging.getLogger()
FEISHU_WEBHOOK_URL = 'https://open.feishu.cn/open-apis/bot/v2/hook/35a2a23c-babc-4675-b792-d4d5cd3ab644'
FEISHU_WEBHOOK_SECRET = 'M4dNCmLgViHdHa5VNyROUc'

login_url = 'https://ikuuu.{}/auth/login'
check_url = 'https://ikuuu.{}/user/checkin'
info_url = 'https://ikuuu.{}/user/profile'
link_url = 'https://ikuuu.{}/user'


header = {
    'origin': 'https://ikuuu.me',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'
}
# <span class="counter">31.11</span> GB
pattern = re.compile('oneclickImport\((.*)\)')
rest_pattern = re.compile('<span class="counter">(.*)</span> GB')
use_pattern = re.compile(r"(.*?),")


def gen_sign(secret, timestamp):
    # 拼接时间戳以及签名校验
    string_to_sign = '{}\n{}'.format(timestamp, secret)

    # 使用 HMAC-SHA256 进行加密
    hmac_code = hmac.new(
        string_to_sign.encode("utf-8"), digestmod=hashlib.sha256
    ).digest()

    # 对结果进行 base64 编码
    sign = base64.b64encode(hmac_code).decode('utf-8')

    return sign


def send_feishu_notification(message, timestamp, session: Session):
    sign = gen_sign(FEISHU_WEBHOOK_SECRET, timestamp)
    headers = {'Content-Type': 'application/json'}
    payload = {'content':
        {
            'text': message
        },
        'timestamp': timestamp,
        'sign': sign,
        "msg_type": "text"
    }
    try:
        session.post(FEISHU_WEBHOOK_URL, headers=headers, json=payload)
    except Exception:
        print('发送飞书通知出错')


def login(emails: list, domain: str):
    for emailInfo in emails:
        if emailInfo is None:
            continue
        email_txt = emailInfo.decode('utf-8')
        if ',' not in email_txt:
            continue
        email2passwd = email_txt.split(',')
        email = email2passwd[0]
        passwd = email2passwd[1]
        session = None
        try:
            data = {
                'email': email,
                'passwd': passwd
            }
            logger.info('email: '+email+' start login')

            session = requests.session()
            pre_get_text = session.get(url=login_url.format(domain), headers=header).text
            if "new domain" in pre_get_text:
                dm_pattern = re.compile(r"https://ikuuu.(.*?)/", re.S)
                dm_list = dm_pattern.findall(pre_get_text)
                return dm_list[0]
            login_res = session.post(url=login_url.format(domain), headers=header, data=data).text
            response = json.loads(login_res)
            result = json.loads(session.post(url=check_url.format(domain), headers=header).text)
            link_text = session.get(link_url.format(domain), headers=header).text
            rest = rest_pattern.findall(link_text)[0]

            rest_proportion_pattern = re.compile("trafficDountChat(.*)?'\n", re.S)

            rest_proportion_pattern_text = rest_proportion_pattern.findall(link_text)
            digit_pattern = re.compile(r'(\d+.*\d*)')
            digit_pattern_res = digit_pattern.findall(rest_proportion_pattern_text[0])
            use_list = use_pattern.findall(rest_proportion_pattern_text[0])
            send_feishu_notification(email + ':' + result['msg'] + ' 使用了' + str(use_list[0]).strip() + ' 剩余流量:' + rest + '，剩余:' + digit_pattern_res[5] + '%', int(datetime.now().timestamp()),
                                     session)
        except Exception as e:
            logger.error('签到失败email: ' + email, e)
            send_feishu_notification(
                "签到失败:" + email + "," + e.__str__(),
                int(datetime.now().timestamp()),
                requests.session())
            return
        finally:
            if session:
                session.close()


if __name__ == '__main__':
    url = 'https://ikuuu.{}/auth/login'
    info = """'(\n        \'1020.51MB\',\n        \'0B\',\n        \'87.23GB\',\n        \'1.13\',\n        \'0.00\',\n        \'98.87\'\n    )\n\n    $(\'.counter\').counterUp({\n        delay: 10,\n        time: 1000\n    });\n\n    function importSublink(client) {\n        if (client === \'quantumult\') {\n"""
    use_pattern = re.compile(r"(.*?),")
    res = use_pattern.findall(info)
    print(str(res[0]).strip())




