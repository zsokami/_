import gzip
import os
import shutil
import subprocess
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import quote

import requests


def download(url, file, unpack_gzip=False):
    os.makedirs(os.path.normpath(os.path.dirname(file)), exist_ok=True)
    with (
        requests.get(url, headers={'Accept-Encoding': 'gzip'}, stream=True) as resp,
        open(file, 'wb') as _out
    ):
        _in = resp.raw
        if unpack_gzip or resp.headers.get('Content-Encoding') == 'gzip':
            _in = gzip.open(_in)
        shutil.copyfileobj(_in, _out)


def test_latency(name, timeout=2000):
    try:
        r = requests.get(f"http://127.0.0.1:9090/proxies/{quote(name, safe='')}/delay", params={
            'url': 'https://i.ytimg.com/generate_204',
            'timeout': timeout
        }, timeout=timeout / 400).json()
    except Exception as e:
        r = {'message': str(e)}
    return r


def test_all_latency(
    config_url: str = None,
    config_path='/etc/clash/config.yaml',
    config_cover=True,
    clash_url='https://github.com/Dreamacro/clash/releases/download/v1.14.0/clash-linux-amd64-v1.14.0.gz',
    clash_path='/usr/local/bin/clash',
    clash_cover=False,
    max_workers=32,
    timeout=2000,
) -> list[tuple[str, dict]]:
    if clash_cover or not os.path.exists(clash_path):
        download(clash_url, clash_path, unpack_gzip=True)
    if config_url and (config_cover or not os.path.exists(config_path)):
        download(config_url, config_path)
    os.chmod(clash_path, 0o755)
    with subprocess.Popen([clash_path, '-f', config_path, '--ext-ctl', ':9090'], stdout=subprocess.PIPE) as popen:
        while b':9090' not in popen.stdout.readline():
            pass
        try:
            proxies = requests.get('http://127.0.0.1:9090/proxies').json()['proxies']
            for k in ('DIRECT', 'REJECT', 'GLOBAL'):
                del proxies[k]
            with ThreadPoolExecutor(max_workers) as executor:
                return sorted(
                    zip(proxies, executor.map(lambda name: test_latency(name, timeout), proxies)),
                    key=lambda x: (x[1].get('meanDelay') or float('inf'), x[1].get('delay') or float('inf'))
                )
        finally:
            popen.terminate()


if __name__ == '__main__':
    for item in test_all_latency('https://dd.al/trial-All', timeout=10000):
        print(*item)
