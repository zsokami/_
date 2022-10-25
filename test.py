import time
import requests

session = requests.session()
# session.trust_env = False  # 禁用系统代理
# session.proxies['http'] = '127.0.0.1:7890'
# session.proxies['https'] = '127.0.0.1:7890'
st = time.time()
with session.get('https://www.google.com/') as res:
    print(time.time() - st)
    print(res.status_code)
st = time.time()
with session.get('https://www.baidu.com/') as res:
    print(time.time() - st)
    print(res.status_code)
import os
print(os.listdir())
with open('test', 'w') as f:
    f.writelines(['test','123'])
print()
print(os.listdir())
