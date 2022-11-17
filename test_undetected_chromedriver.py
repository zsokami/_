import requests
from bs4 import BeautifulSoup
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait
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
    print('get...')
    chrome.get(url)
    print('get done')
    wait = WebDriverWait(chrome, 8)
    try:
        wait.until_not(ec.title_is('Just a moment...'))
        wait.until_not(ec.title_is(''))
        print('title is not "Just a moment..." and not empty')
    except TimeoutException:
        print('WebDriverWait timeout')
    sess = Session(user_agent=chrome.execute_script('return navigator.userAgent'))
    sess.cookies.update((cookie['name'], cookie['value']) for cookie in chrome.get_cookies())
    chrome.quit()
    print(sess.headers)
    print(sess.cookies.get_dict())
    doc = BeautifulSoup(sess.get(url).text, 'html.parser')
    print(doc.title)
