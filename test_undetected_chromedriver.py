from time import time, sleep

import requests
from bs4 import BeautifulSoup
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait
from selenium_stealth import stealth
from undetected_chromedriver import Chrome


class Session(requests.Session):
    def __init__(
        self,
        host=None,
        use_proxy=False,
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'
    ):
        super().__init__()
        if use_proxy:
            self.trust_env = False  # 禁用系统代理
            self.proxies['http'] = self.proxies['https'] = '127.0.0.1:7890'
        self.headers['User-Agent'] = user_agent
        self.base = 'https://' + host if host else ''
        self.host = host


if __name__ == '__main__':
    # url = 'https://nowsecure.nl'
    # url = 'https://kuainiao.top'
    url = 'https://purefast.net'
    chrome = Chrome()
    stealth(
        chrome,
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36',
        languages=['zh-CN', 'zh'],
        vendor="Google Inc.",
        platform="Win32",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine"
    )
    print('get...')
    chrome.get(url)
    print('get done, wait...')
    wait = WebDriverWait(chrome, 8)
    try:
        st = time()
        wait.until_not(ec.title_is('Just a moment...'))
        wait.until_not(ec.title_is(''))
        print('WebDriverWait', time() - st, 'seconds')
        print('title is not "Just a moment..." and not empty')
    except TimeoutException:
        print('WebDriverWait timeout')
    sess = Session(user_agent=chrome.execute_script('return navigator.userAgent'))
    for key in ['cf_clearance', 'ge_ua_key']:
        cookie = chrome.get_cookie(key)
        sess.cookies[key] = cookie['value']
    chrome.quit()
    print(sess.headers)
    print(sess.cookies.get_dict())
    doc = BeautifulSoup(sess.get(url).text, 'html.parser')
    print(doc.title)
