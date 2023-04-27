import requests
print(requests.get('http://localhost/sub?target=clash&list=true&udp=true&scv=true&config=https://raw.githubusercontent.com/zsokami/ACL4SSR/main/ACL4SSR_Online_Full_Mannix.ini&url=https://paste.wmlabs.net/raw/82965bb7b5a3').text)

print(requests.get('http://localhost/sub?target=clash&list=true&udp=true&scv=true&config=https://raw.githubusercontent.com/zsokami/ACL4SSR/main/ACL4SSR_Online_Full_Mannix.ini&url=https://api.hkspeedup.com/subscribe/74rk9uwk6m').text)
