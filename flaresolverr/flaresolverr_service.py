import logging
import time
from urllib.parse import unquote

from selenium.common import TimeoutException, StaleElementReferenceException, NoSuchElementException
from selenium.webdriver.chrome.webdriver import WebDriver
from undetected_chromedriver import WebElement
from selenium.webdriver.common.by import By
from selenium.webdriver.support.expected_conditions import (
    presence_of_element_located, title_is, any_of, none_of, all_of, visibility_of)
# from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.wait import WebDriverWait

import utils
from dtos import (STATUS_OK, ChallengeResolutionResultT,
                  ChallengeResolutionT, V1RequestBase)

ACCESS_DENIED_TITLES = [
    # Cloudflare
    'Access denied',
    # Cloudflare http://bitturk.net/ Firefox
    'Attention Required! | Cloudflare'
]
ACCESS_DENIED_SELECTORS = [
    # Cloudflare
    'div.cf-error-title span.cf-code-label span',
    # Cloudflare http://bitturk.net/ Firefox
    '#cf-error-details div.cf-error-overview h1'
]
CHALLENGE_TITLES = [
    # Cloudflare
    'Just a moment...',
    '请稍候…',
    # DDoS-GUARD
    'DDoS-Guard',
    # Other
    '安全网关检测中',
    # Empty title
    '',
]
CHALLENGE_SELECTORS = [
    # Cloudflare
    '#cf-challenge-running', '.ray_id', '.attack-box', '#cf-please-wait', '#challenge-spinner', '#trk_jschal_js',
    # Custom CloudFlare for EbookParadijs, Film-Paleis, MuziekFabriek and Puur-Hollands
    'td.info #js_info',
    # Fairlane / pararius.com
    'div.vc div.text-box h2'
]
SHORT_TIMEOUT = 10
LONG_TIMEOUT = 60
POLL_FREQUENCY = 0.1


def find(self: WebDriver | WebElement, css_selector: str, timeout: float = 0, period=0.1):
    end_time = time.monotonic() + timeout - period if timeout >= 0 else float('inf')
    while True:
        try:
            return self.find_element(By.CSS_SELECTOR, css_selector)
        except NoSuchElementException:
            if time.monotonic() >= end_time:
                return None
            time.sleep(period)


def find_all(self: WebDriver | WebElement, css_selector: str, timeout: float = 0, period=0.1):
    end_time = time.monotonic() + timeout - period if timeout >= 0 else float('inf')
    while True:
        elements = self.find_elements(By.CSS_SELECTOR, css_selector)
        if elements or time.monotonic() >= end_time:
            return elements
        time.sleep(period)


def click_verify(driver: WebDriver, wait_verify_box=False):
    try:
        selector_iframe = "iframe[title='Widget containing a Cloudflare security challenge']"
        if wait_verify_box:
            logging.debug("Waiting for the Cloudflare verify iframe")
            iframe = find(driver, selector_iframe, SHORT_TIMEOUT)
        else:
            logging.debug("Try to find the Cloudflare verify iframe")
            iframe = find(driver, selector_iframe)
        if not iframe:
            raise Exception("Not found Cloudflare verify iframe")

        driver.switch_to.frame(iframe)
        challenge = find(driver, '#challenge-stage')
        success = find(driver, '#success')
        fail = find(driver, '#fail')
        expired = find(driver, '#expired')
        stages = (challenge, success, fail, expired)
        if not all(stages):
            raise Exception(f"(challenge, success, fail, expired) == {stages}")

        try:
            WebDriverWait(driver, LONG_TIMEOUT, POLL_FREQUENCY).until(any_of(*map(visibility_of, stages)))
        except TimeoutException:
            raise Exception("Timeout waiting for result of Cloudflare verify")
        except StaleElementReferenceException:
            return False
        if success.is_displayed():
            logging.debug("Cloudflare verify success")
            return True
        elif fail.is_displayed():
            logging.debug("Cloudflare verify fail")
            return False
        elif expired.is_displayed():
            logging.debug("Cloudflare verify expired")
            return False

        checkbox = find(challenge, 'input')
        if not checkbox:
            raise Exception("Not found checkbox in #challenge-stage")
        checkbox.click()
        # actions = ActionChains(driver)
        # actions.move_to_element_with_offset(checkbox, 5, 7)
        # actions.click(checkbox)
        # actions.perform()
        logging.debug("Cloudflare verify checkbox clicked")

        stages = (success, fail, expired)
        try:
            WebDriverWait(driver, LONG_TIMEOUT, POLL_FREQUENCY).until(any_of(*map(visibility_of, stages)))
        except TimeoutException:
            raise Exception("Timeout waiting for result of Cloudflare verify")
        except StaleElementReferenceException:
            return False
        if success.is_displayed():
            logging.debug("Cloudflare verify success")
            return True
        elif fail.is_displayed():
            logging.debug("Cloudflare verify fail")
        else:
            logging.debug("Cloudflare verify expired")
    except Exception as e:
        logging.debug(f"Error: {e}")
    finally:
        driver.switch_to.default_content()
    return False


def evil_logic(req: V1RequestBase, driver: WebDriver, method: str) -> ChallengeResolutionT:
    res = ChallengeResolutionT({})
    res.status = STATUS_OK
    res.message = ""

    # navigate to the page
    logging.debug(f'Navigating to... {req.url}')
    if method == 'POST':
        post_request(req, driver)
    else:
        driver.get(req.url)
    if utils.get_config_log_html():
        logging.debug(f"Response HTML:\n{driver.page_source}")

    page_title = driver.title

    # find access denied titles
    for title in ACCESS_DENIED_TITLES:
        if title == page_title:
            raise Exception('Cloudflare has blocked this request. '
                            'Probably your IP is banned for this site, check in your web browser.')
    # find access denied selectors
    for selector in ACCESS_DENIED_SELECTORS:
        found_elements = driver.find_elements(By.CSS_SELECTOR, selector)
        if len(found_elements) > 0:
            raise Exception('Cloudflare has blocked this request. '
                            'Probably your IP is banned for this site, check in your web browser.')

    # find challenge by titles
    challenge_found = False
    wait_verify_box = False
    if find(driver, '.cf-turnstile'):
        challenge_found = True
        wait_verify_box = True
        logging.info("Challenge detected. Selector found: .cf-turnstile")
    else:
        for title in CHALLENGE_TITLES:
            if title.lower() == page_title.lower():
                challenge_found = True
                if not page_title:
                    logging.info("Challenge detected. Empty title")
                else:
                    logging.info("Challenge detected. Title found: " + page_title)
                break
        else:
            # find challenge by selectors
            for selector in CHALLENGE_SELECTORS:
                found_elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if len(found_elements) > 0:
                    challenge_found = True
                    logging.info("Challenge detected. Selector found: " + selector)
                    break

    if challenge_found:
        wait = WebDriverWait(driver, SHORT_TIMEOUT, POLL_FREQUENCY)
        not_verify_box = none_of(
            presence_of_element_located((By.CSS_SELECTOR, '.cf-turnstile')),
            presence_of_element_located((By.CSS_SELECTOR, "#turnstile-wrapper")),
        )
        waiting = all_of(
            any_of(
                *map(title_is, CHALLENGE_TITLES),
                *(presence_of_element_located((By.CSS_SELECTOR, selector)) for selector in CHALLENGE_SELECTORS)
            ),
            not_verify_box
        )
        attempt = 0
        while True:
            try:
                attempt += 1
                # wait until the title changes and all the selectors disappear
                logging.debug("Waiting for titles and selectors (attempt " + str(attempt) + ")")
                wait.until_not(waiting)
                if not_verify_box(driver):
                    break
                if click_verify(driver, wait_verify_box):
                    break
            except TimeoutException:
                pass
        logging.info("Challenge solved!")
        res.message = "Challenge solved!"
    else:
        logging.info("Challenge not detected!")
        res.message = "Challenge not detected!"

    challenge_res = ChallengeResolutionResultT({})
    challenge_res.url = driver.current_url
    challenge_res.status = 200  # todo: fix, selenium not provides this info
    challenge_res.cookies = driver.get_cookies()
    challenge_res.userAgent = driver.execute_script("return navigator.userAgent")

    if not req.returnOnlyCookies:
        challenge_res.headers = {}  # todo: fix, selenium not provides this info
        challenge_res.response = driver.page_source

    res.result = challenge_res
    return res


def post_request(req: V1RequestBase, driver: WebDriver):
    post_form = f'<form id="hackForm" action="{req.url}" method="POST">'
    query_string = req.postData if req.postData[0] != '?' else req.postData[1:]
    pairs = query_string.split('&')
    for pair in pairs:
        parts = pair.split('=')
        # noinspection PyBroadException
        try:
            name = unquote(parts[0])
        except Exception:
            name = parts[0]
        if name == 'submit':
            continue
        # noinspection PyBroadException
        try:
            value = unquote(parts[1])
        except Exception:
            value = parts[1]
        post_form += f'<input type="text" name="{name}" value="{value}"><br>'
    post_form += '</form>'
    html_content = f"""
        <!DOCTYPE html>
        <html>
        <body>
            {post_form}
            <script>document.getElementById('hackForm').submit();</script>
        </body>
        </html>"""
    driver.get("data:text/html;charset=utf-8," + html_content)
