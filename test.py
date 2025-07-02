from bs4 import BeautifulSoup
import requests
import pandas as pd
def safe_find_text(parent, tag, class_=None, id_=None, default=''):
    if parent:
        if id_:
            el = parent.find(tag, id=id_)
        elif class_:
            el = parent.find(tag, class_=class_)
        else:
            el = parent.find(tag)
        return el.text.strip() if el else default
    return default

url = 'https://sacramento.craigslist.org/cto/d/rio-linda-2007-honda-odyssey-ex-clean/7862338073.html'
response = requests.get(url)
html = response.content
soup = BeautifulSoup(html, 'html.parser')

# Try printing structure to find posted date
actions_div = soup.find('section', class_='body')
posted_date = safe_find_text(actions_div, 'time', class_='date timeago')
print(f"Posted date: {pd.to_datetime(posted_date)}")
