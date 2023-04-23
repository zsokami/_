from func_timeout import FunctionTimedOut, func_timeout

from dtos import V1RequestBase
from flaresolverr_service import evil_logic
from utils import get_webdriver

if __name__ == '__main__':
    with get_webdriver() as chrome:
        req = V1RequestBase({'url': 'https://nowsecure.nl/'})
        timeout = 30
        try:
            func_timeout(timeout, evil_logic, (req, chrome, 'GET'))
        except FunctionTimedOut:
            raise Exception(f'Error solving the challenge. Timeout after {timeout} seconds.')
        except Exception as e:
            raise Exception('Error solving the challenge. ' + str(e))
        print(chrome.title)
