import requests
from base64 import urlsafe_b64encode
sub = '''proxies:
- {name: V1 🇭🇰香港1 IPLC 倍率1x, server: s.hkspeedup.com, port: 4001, type: ss, cipher: aes-256-gcm, password: lr62zu22w7, udp: true}
'''
print(requests.get('http://localhost/sub?target=clash&list=true&udp=true&scv=true&config=https://raw.githubusercontent.com/zsokami/ACL4SSR/main/ACL4SSR_Online_Full_Mannix.ini&url=data:text/plain;base64,'+urlsafe_b64encode(sub.encode()).decode()).text)

print(requests.get('http://localhost/sub?target=clash&list=true&udp=true&scv=true&config=https://raw.githubusercontent.com/zsokami/ACL4SSR/main/ACL4SSR_Online_Full_Mannix.ini&url=https://api.hkspeedup.com/subscribe/74rk9uwk6m').text)
