import requests
from loguru import logger
import re


class taobao(object):
    def __init__(self, username, encrypt_psd, ua):
        self.username = username
        self.encrypt_psd = encrypt_psd
        self.ua = ua
        self.session = requests.Session()

        self.check_url = 'https://login.taobao.com/newlogin/account/check.do?appName=taobao&fromSite=0'
        self.login_url = 'https://login.taobao.com/newlogin/login.do?appName=taobao&fromSite=0'
        self.my_info_url = 'https://i.taobao.com/my_taobao.htm'
        self.timeout = 3

    def login(self):
        # 第一步，检查是否有滑块验证码
        if not self.check_user():
            logger.error('未通过淘宝的检查，请检查链接,用户名和ua值是否正确')
            return
        logger.info('检测正常，未需要验证码')

        # 第二步，检查账号密码,获取申请st码地址
        st_url = self.check_password()
        if st_url.strip() == '':
            logger.error('检查账号、密码和ua是否正确')
            return
        logger.info('获取申请st码地址成功,地址为：'+ st_url)

        # 第三步，访问st码地址,获取cookie
        self.apply_st(st_url)
        logger.info('访问st地址正常')

        # 第四步，获取昵称检查是否登录成功
        nickname = self.get_nickname()
        if nickname:
            logger.info('登录成功，昵称为:' + nickname)
        else:
            logger.error('获取昵称失败')

    def check_user(self):
        data = {
            'loginId': self.username,
            'ua': self.ua
        }
        res = self.session.post(self.check_url, data=data, timeout=self.timeout)
        if res.status_code != 200:
            return False
        res_json = res.json()
        if res_json['content']['data'].get('isCheckCodeShowed', 'False') == 'True':
            return False
        return True

    def check_password(self):
        header = {
            'accept': 'application/json, text/plain, */*',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,vi;q=0.7',
            'content-type': 'application/x-www-form-urlencoded',
            'referer': 'https://login.taobao.com/member/login.jhtml?spm=a21bo.2017.754894437.1.5af911d9vMNRvs&f=top&redirectURL=https%3A%2F%2Fwww.taobao.com%2F',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36'
        }

        data = {
            'loginId': self.username,
            'password2': self.encrypt_psd,
            'keepLogin': 'true',
            'ua': self.ua,
            'umidGetStatusVal': '255',
            'screenPixel': '1440x960',
            'navlanguage': 'zh-CN',
            'navUserAgent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36',
            'navPlatform': 'Win32',
            'appName': 'taobao',
            'appEntrance': 'taobao_pc',
            '_csrf_token': '6VM7C3lZN3dYnXX09GsPs3',
            'umidToken': '4e8ef7f445e142345bccfa23d659b1e1b162f31b',
            'hsiz': '1b33cd3c5f0c870bd15c6e7c43750f5f',
            'bizParams': '',
            'style': 'default',
            'appkey': '00000000',
            'from': 'tbTop',
            'isMobile': 'false',
            'lang': 'zh_CN',
            'returnUrl': 'https://www.taobao.com/',
            'fromSite': '0'
        }
        res = self.session.post(self.login_url, data=data, headers=header)
        res = res.json()
        url = ''
        try:
            url = res['content']['data']['asyncUrls'][0]
        except:
            logger.error('获取st码url失败')
        return url

    def apply_st(self, st_url):
        header = {
            'accept': 'application/json, text/plain, */*',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,vi;q=0.7',
            'content-type': 'application/x-www-form-urlencoded',
            'referer': 'https://login.taobao.com/member/login.jhtml?spm=a21bo.2017.754894437.1.5af911d9vMNRvs&f=top&redirectURL=https%3A%2F%2Fwww.taobao.com%2F',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36'
        }
        self.session.get(st_url)

    def get_nickname(self):
        header = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,vi;q=0.7',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'none',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36'
        }
        response = self.session.get(self.my_info_url, headers=header)
        m = re.search(r'<input id="mtb-nickname" type="hidden" value="(.*?)"/>', response.text)
        if m:
            return m.group(1)
        return ''


if __name__ == '__main__':
    # username改成自己的用户名，密码和ua从浏览器或抓包软件获取填入
    username = 'username'
    encrypt_psd = '1dbb690bdb3f0d0d0e02895732a33e443c194a0ca5f1c9addbaeeac359de51f745eb6d7950ecdf203eb3f6c770747af7efbe6296eea7e906a3ef924f5e2e1a93fb911393ebc850de671c2e93a584592c6b6ea9f2d5c70af78efe4ba45373d5f1ca1352b0cc58b8210b677f4ef9e2df9a568e6f6680c3ba1f43f9d08fa8377721'
    ua = '123#lcQDbF6mtT5ugQbxlDnv8ldEzQXHO1A9926XYQledl/HzaHKDF8u/cqgsxIMrJOqvsyx9v0qgiWpmoExvoReQ0sfnZBKxpO5dPiuU1GZKNWMk4JeNjodGv1EGDYppGMXMFw2ClMB7OEPMrNRVQckiKRo1XvZFYyGfoBsb7LegzBJvojwi5OqrREYzBilTBEfqChqhzMOU+73J623vqnqWKPMYWtF/c9XMOjGZvyUerSGKOBigpHJaTKYGDU9Fj4ojlPW6TCcpoumpelej9WOhEqVSG3q3bETkfoefE+w/sZT3SBwlcB0dRzUkGn5uds3T9fD1xDTkvFnAhwmDJiX8+E+guOSaJCn0G9sFNRn630oqZrJ5By5GnAuJAdkKATJZeVKuvt2W/Psd+BXbU8ngySr+5agU+em3D9i/Pon4wXgXjyGm6ywtFUzqmvoTGEbszP3MGlyRLqPplY8wwTTd7EDe2GkfKAgmrLRc6SrdzYrTHWsRn04kb1rAFDSYZNbZvHwh9JHlToqBLd1FPqSEpjqo5bSxikHDuY1rRRP5oknvR+76rKlbhy6fDqqr497cz1iIczllmPEyDncTQjDhOh+XK9t8TbyYZcVedAGt9lX80HpSMdmEpBU5tO6l8bivx/JEM90vs5sEYMOZWr6ee8pckzgNA13g3neKWphHCMACyGYfjF7MJMYrs0X+HF9elVS1gdIULqTJFNgwXeRtWGN5RezqJBs8csTmuRPvWfZ+nrTiSzXXE/LKfnrsV20NAH1W83qRTwrQ8BVTIyK3Q7PmR8TAIuXvQtJkUguL53vsS+yCG+HHva4idvtQyz0PZRchFidlSrksfGvX88gQ7nZ3UTMIlHVn3ivKazKbgjrTcMX98nA2rxtxLaSFEftfxPB+uBBnEiXK97zmlIKlgCutqrsyZHq2O4uvVv7mh+U1mGP1ifuZ1xOJUoQr+Kg3RkfDQ3aGFQLtzra4x2Vc90='
    tb = taobao(username=username, encrypt_psd=encrypt_psd, ua=ua)
    tb.login()