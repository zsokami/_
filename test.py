import os
import time
from datetime import datetime
from subprocess import getoutput

import requests

session = requests.session()
# session.trust_env = False  # 禁用系统代理
# session.proxies['http'] = '127.0.0.1:7890'
# session.proxies['https'] = '127.0.0.1:7890'

print(os.getenv('GITHUB_SHA'))
print(getoutput('git rev-parse HEAD'))
print(
    session.get(
        f"https://api.github.com/repos/{os.getenv('GITHUB_REPOSITORY')}/git/{os.getenv('GITHUB_REF')}",
        headers={'Authorization': f"Bearer {os.getenv('GITHUB_TOKEN')}"}
    ).json()['object']['sha']
)

st = time.time()
with session.get('https://www.google.com/') as res:
    print(time.time() - st)
    print(res.status_code)
st = time.time()
with session.get('https://www.baidu.com/') as res:
    print(time.time() - st)
    print(res.status_code)

print(os.listdir())
print(datetime.fromtimestamp(os.path.getmtime('test')))
with open('test', 'w') as f:
    f.writelines(['test', str(time.time())])
print()
print(os.listdir())
print(datetime.fromtimestamp(os.path.getmtime('test')))
