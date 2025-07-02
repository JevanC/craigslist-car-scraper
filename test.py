from bs4 import BeautifulSoup
import requests
import pandas as pd
response = requests.get(
    "https://proxy.webshare.io/api/v2/proxy/list/?mode=direct&page=1&page_size=25",
    headers={"Authorization": "Token g7wtr2z46gt7mt2x2c68kaw7yn73b2gi9p5zy9fl"}
)
 
print([f"{i['proxy_address']}:{i['port']}:{i['username']}:{i['password']}" for i in response.json()['results']])