import os
from concurrent.futures import ThreadPoolExecutor
from time import sleep
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait
from seleniumwire.undetected_chromedriver import Chrome, ChromeOptions

use_proxy = False

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

    def request(self, method, url, **kwargs):
        return super().request(method, urljoin(self.base, url), **kwargs)

    def get_ip_info(self):
        """return (ip, 位置, 运营商)"""
        addr = self.get(f'https://ip125.com/api/{self.get("https://ident.me").text}?lang=zh-CN').json()
        return (
            addr['query'],
            addr['country'] + (',' + addr['city'] if addr['city'] and addr['city'] != addr['country'] else ''),
            addr['isp'] + (',' + addr['org'] if addr['org'] and addr['org'] != addr['isp'] else '')
        )


if __name__ == '__main__':
    urls = ['https://purefast.net']#, 'https://nowsecure.nl', 'https://kuainiao.top']

    def test(url):
        options = ChromeOptions()
        options.add_argument(
            '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'
        )
        options.page_load_strategy = 'eager'

        seleniumwire_options = None
        if use_proxy:
            seleniumwire_options = {
                'proxy': {
                    'http': 'http://127.0.0.1:7890',
                    'https': 'https://127.0.0.1:7890',
                }
            }

        chrome = Chrome(
            options=options,
            seleniumwire_options=seleniumwire_options,
            driver_executable_path=os.path.join(os.getenv('CHROMEWEBDRIVER'), 'chromedriver')
        )

        wait = WebDriverWait(chrome, 20)
        res, nTries, nTimeout = None, 0, 0
        try:
            for nTries in range(1, 2):
                # print(f'get {url}')
                chrome.get(url)
                if chrome.title not in ('Just a moment...', ''):
                    print(f"chrome.title not in ('Just a moment...', ''), is {chrome.title}")
                # print('get done, wait...')
                try:
                    # st = time()
                    wait.until_not(ec.any_of(ec.title_is('Just a moment...'), ec.title_is('')))
                    # print('WebDriverWait', time() - st, 'seconds')
                    # print('title is not "Just a moment..." and not empty')
                except TimeoutException:
                    # print('WebDriverWait timeout')
                    nTimeout += 1
                    continue

                chrome_headers = None
                for req in chrome.iter_requests():
                    if req.path == '/':
                        chrome_headers = req.headers
                print('chrome_headers', chrome_headers.as_string())

                sess = Session(use_proxy=use_proxy, user_agent=chrome.execute_script('return navigator.userAgent'))
                for key in ['cf_clearance', 'ge_ua_key']:
                    cookie = chrome.get_cookie(key)
                    if cookie:
                        sess.cookies[key] = cookie['value']
                
                # for name in ['cookie', 'cache-control', 'accept', 'accept-language']:
                #     sess.headers[name] = chrome_headers[name]
                
                # removed = {'upgrade-insecure-requests','user-agent','referer','accept-language','accept-encoding','cache-control'}

                # for k, v in chrome_headers.items():
                #     if k.startswith('sec-'):
                #         continue
                #     if k in removed:
                #         continue
                #     sess.headers[k] = v
                sess.headers['accept'] = chrome_headers['accept']
                
                # sess.headers.update(chrome_headers.items())

                # print(sess.headers['User-Agent'])
                # print(sess.cookies.get_dict())
                sess_res = sess.get(url)

                print('session_headers', sess_res.request.headers)

                doc = BeautifulSoup(sess_res.text, 'html.parser')
                
                # print(doc.title)
                if doc.title.text not in ('Just a moment...', ''):
                    res = doc.title
                    break
                
        except Exception as e:
            res = e
        chrome.quit()
        return res, nTries, nTimeout

    with ThreadPoolExecutor(32) as executor:
        for res, nTries, nTimeout in executor.map(test, urls):
            print(res, nTries, nTimeout)
