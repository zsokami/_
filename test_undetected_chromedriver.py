import os
from concurrent.futures import ThreadPoolExecutor
# from time import time

import requests
from bs4 import BeautifulSoup
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait
from undetected_chromedriver import Chrome, ChromeOptions

use_proxy = True


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
    urls = ['https://purefast.net', 'https://nowsecure.nl', 'https://kuainiao.top']

    def test(url):
        options = ChromeOptions()
        options.add_argument(
            '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'
        )
        options.page_load_strategy = 'eager'
        chrome = Chrome(
            options=options,
            driver_executable_path=os.path.join(os.getenv('CHROMEWEBDRIVER'), 'chromedriver')
        )
        wait = WebDriverWait(chrome, 20)
        try:
            for nRetries in range(10):
                # print(f'get {url}')
                chrome.get(url)
                # print('get done, wait...')
                try:
                    # st = time()
                    wait.until_not(ec.any_of(ec.title_is('Just a moment...'), ec.title_is('')))
                    # print('WebDriverWait', time() - st, 'seconds')
                    # print('title is not "Just a moment..." and not empty')
                except TimeoutException:
                    # print('WebDriverWait timeout')
                    continue
                sess = Session(use_proxy=use_proxy, user_agent=chrome.execute_script('return navigator.userAgent'))
                for key in ['cf_clearance', 'ge_ua_key']:
                    cookie = chrome.get_cookie(key)
                    if cookie:
                        sess.cookies[key] = cookie['value']
                # print(sess.headers['User-Agent'])
                # print(sess.cookies.get_dict())
                doc = BeautifulSoup(sess.get(url).text, 'html.parser')
                # print(doc.title)
                if doc.title.text not in ('Just a moment...', ''):
                    return doc.title, nRetries
            return None, nRetries
        except Exception as e:
            return e, nRetries
        finally:
            chrome.quit()

    with ThreadPoolExecutor(32) as executor:
        for res, nRetries in executor.map(test, urls):
            print(res, nRetries)
