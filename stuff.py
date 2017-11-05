import requests
import requests.auth

client_auth = requests.auth.HTTPBasicAuth('XT6SZJFNEZHiTg', 'FMAfyywwaCfiAX2Qq-1me8YBwmY')
post_data = {"grant_type": "password", "username": "Nithishbn", "password": "z3eIV2HFggndpjPy"}
headers = {"User-Agent": "ImageScrapper/0.1 by Nithishbn"}
response = requests.post("https://www.reddit.com/api/v1/access_token", auth=client_auth, data=post_data,
                         headers=headers)
print(response.json())
