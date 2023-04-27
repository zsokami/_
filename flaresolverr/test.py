import logging
import os
import sys
from func_timeout import FunctionTimedOut, func_timeout

from dtos import V1RequestBase
from flaresolverr_service import evil_logic, click_verify, find
import utils

if __name__ == '__main__':
    # os.environ.update(
    #     http_proxy='http://127.0.0.1:7890',
    #     https_proxy='http://127.0.0.1:7890',
    #     HEADLESS='false',
    # )
    # configure logger
    log_level = 'DEBUG'
    # log_level = os.environ.get('LOG_LEVEL', 'info').upper()
    logger_format = '%(asctime)s %(levelname)-8s %(message)s'
    if log_level == 'DEBUG':
        logger_format = '%(asctime)s %(levelname)-8s ReqId %(thread)s %(message)s'
    logging.basicConfig(
        format=logger_format,
        level=log_level,
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    # disable warning traces from urllib3
    logging.getLogger('urllib3').setLevel(logging.ERROR)
    logging.getLogger('selenium.webdriver.remote.remote_connection').setLevel(logging.WARNING)
    logging.getLogger('undetected_chromedriver').setLevel(logging.WARNING)

    logging.debug('Debug log enabled')

    chrome = utils.get_webdriver()
    timeout = 60
    try:
        for url in [
            'https://google.com',
            'https://nowsecure.nl',
            'https://chat.openai.com',
            'https://purefast.net',
            'https://airfree.app',
            'https://youxiniang.top',
        ]:
            res = func_timeout(timeout, evil_logic, (V1RequestBase({'url': url}), chrome, 'GET'))
            print(chrome.title)
    except FunctionTimedOut:
        raise Exception(f'{url} Error solving the challenge. Timeout after {timeout} seconds.')
    except Exception as e:
        raise Exception(f'{url} Error solving the challenge. {e}')
    finally:
        chrome.quit()
