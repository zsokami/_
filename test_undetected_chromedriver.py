from time import sleep, time

import requests
from bs4 import BeautifulSoup
from undetected_chromedriver import Chrome


class Session(requests.Session):
    def __init__(
        self,
        host=None,
        use_proxy=False,
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36'
    ):
        super().__init__()
        if use_proxy:
            self.trust_env = False  # 禁用系统代理
            self.proxies['http'] = self.proxies['https'] = '127.0.0.1:7890'
        self.headers['User-Agent'] = user_agent
        self.base = 'https://' + host if host else ''
        self.host = host


if __name__ == '__main__':
    url = 'https://nowsecure.nl'
    chrome = Chrome()
    print('get...')
    chrome.get(url)
    print('get done')
    end = time() + 8
    while not chrome.get_cookie('cf_clearance'):
        if time() > end:
            break
        sleep(0.1)
    sess = Session(user_agent=chrome.execute_script('return navigator.userAgent'))
    sess.cookies.update((cookie['name'], cookie['value']) for cookie in chrome.get_cookies())
    chrome.quit()
    print(sess.headers)
    print(sess.cookies.get_dict())
    doc = BeautifulSoup(sess.get(url).text, 'html.parser')
    print(doc.title)
