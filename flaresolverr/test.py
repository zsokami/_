import logging
import os
import sys
from func_timeout import FunctionTimedOut, func_timeout

from dtos import V1RequestBase
from flaresolverr_service import evil_logic
import utils

if __name__ == '__main__':
    # configure logger
    log_level = os.environ.get('LOG_LEVEL', 'info').upper()
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

    with utils.get_webdriver() as chrome:
        req = V1RequestBase({'url': 'https://nowsecure.nl/'})
        timeout = 30
        try:
            func_timeout(timeout, evil_logic, (req, chrome, 'GET'))
        except FunctionTimedOut:
            raise Exception(f'Error solving the challenge. Timeout after {timeout} seconds.')
        except Exception as e:
            raise Exception('Error solving the challenge. ' + str(e))
        print(chrome.title)
