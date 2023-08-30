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

login_url = 'https://ikuuu.art/auth/login'
check_url = 'https://ikuuu.art/user/checkin'
info_url = 'https://ikuuu.art/user/profile'
link_url = 'https://ikuuu.art/user'


header = {
    'origin': 'https://ikuuu.art',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'
}
# <span class="counter">31.11</span> GB
pattern = re.compile('oneclickImport\((.*)\)')
rest_pattern = re.compile('<span class="counter">(.*)</span> GB')


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


def login(emails: list):
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
            response = json.loads(session.post(url=login_url, headers=header, data=data).text)
            result = json.loads(session.post(url=check_url, headers=header).text)
            link_text = session.get(link_url, headers=header).text
            rest = rest_pattern.findall(link_text)[0]
            send_feishu_notification(email + ':' + result['msg'] + ' 剩余流量:' + rest, int(datetime.now().timestamp()),
                                     session)
        except Exception as e:
            logger.error('签到失败email: ' + email, e)
        finally:
            if session:
                session.close()


if __name__ == '__main__':
    pass
    # for eminfo in list_emails:
    #     lst = [_ for _ in eminfo.values()]
    #     res = ','.join(lst)
    #     print('zadd emails 0 '+res)




