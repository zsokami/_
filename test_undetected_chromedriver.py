from time import time, sleep

import requests
from bs4 import BeautifulSoup
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait
from selenium_stealth import stealth
from seleniumwire.undetected_chromedriver import Chrome, ChromeOptions
from seleniumwire.request import Request
import os


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


def interceptor(request: Request):
    if 'cookie' in request.headers:
        request.abort()


if __name__ == '__main__':
    url = 'https://google.com'
    # url = 'https://bot.sannysoft.com/'
    # url = 'https://nowsecure.nl'
    # url = 'https://kuainiao.top'
    # url = 'https://purefast.net'
    options = ChromeOptions()
    # options.add_experimental_option('prefs', {'profile.managed_default_content_settings.images': 2})
    options.page_load_strategy = 'eager'
    chrome = Chrome(options=options, driver_executable_path=os.getenv('CHROMEWEBDRIVER'))
    # chrome.request_interceptor = interceptor
    # stealth(
    #     chrome,
    #     user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36',
    #     languages=['zh-CN', 'zh'],
    #     vendor="Google Inc.",
    #     platform="Win32",
    #     webgl_vendor="Intel Inc.",
    #     renderer="Intel Iris OpenGL Engine"
    # )
    print('get...')
    chrome.get(url)
    print('get done, wait...')
    print(chrome.title)
    # print('get done, wait...')
    # sleep(10)
    # wait = WebDriverWait(chrome, 10)
    # try:
    #     st = time()
    #     wait.until_not(ec.any_of(ec.title_is('Just a moment...'), ec.title_is('')))
    #     print('WebDriverWait', time() - st, 'seconds')
    #     print('title is not "Just a moment..." and not empty')
    # except TimeoutException:
    #     print('WebDriverWait timeout')
    # sess = Session(use_proxy=True)
    # for key in ['cf_clearance', 'ge_ua_key']:
    #     cookie = chrome.get_cookie(key)
    #     if cookie:
    #         sess.cookies[key] = cookie['value']
    # for request in chrome.iter_requests():
    #     if request.path == '/':
    #         print(request.headers)
    #         headers = request.headers
    #     if request.response:
    #         print(
    #             request.url,
    #             request.response.status_code,
    #             request.response.headers['Content-Type']
    #         )
    chrome.quit()
    # sess.headers.update(headers)
    # print(sess.headers)
    # print(sess.cookies.get_dict())
    # doc = BeautifulSoup(sess.get(url).text, 'html.parser')
    # print(doc.title)
