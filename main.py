from bs4 import BeautifulSoup
import pandas as pd
import requests
from google.genai import types
import ast
from google import genai
import re
import json
import sqlite3
import time
import random

header_pool = [
    {
        "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                       "AppleWebKit/537.36 (KHTML, like Gecko) "
                       "Chrome/126.0.0.0 Safari/537.36"),
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.google.com/",
    },
    {
        "User-Agent": ("Mozilla/5.0 (Macintosh; Intel Mac OS X 13_6_1) "
                       "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 "
                       "Safari/605.1.15"),
        "Accept-Language": "en-US,en;q=0.8",
        "Referer": "https://duckduckgo.com/",
    },
    {
        "User-Agent": ("Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:128.0) "
                       "Gecko/20100101 Firefox/128.0"),
        "Accept-Language": "en-US,en;q=0.7",
        "Referer": "https://www.bing.com/",
    },
    {
        "User-Agent": ("Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) "
                       "AppleWebKit/605.1.15 (KHTML, like Gecko) "
                       "CriOS/126.0.0.0 Mobile/15E148 Safari/604.1"),
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.google.com/",
    },
]
gemini_key = 'AIzaSyCE9DGTfnYHxPULyY6NIuj6sgMnNAZnuoY'
client = genai.Client(api_key=gemini_key)
raw_proxies = [
    "198.23.239.134:6540:amkdfvil:wrpirhjyvz97",
    "207.244.217.165:6712:amkdfvil:wrpirhjyvz97",
    "107.172.163.27:6543:amkdfvil:wrpirhjyvz97",
    "23.94.138.75:6349:amkdfvil:wrpirhjyvz97",
    "216.10.27.159:6837:amkdfvil:wrpirhjyvz97",
    "136.0.207.84:6661:amkdfvil:wrpirhjyvz97",
    "64.64.118.149:6732:amkdfvil:wrpirhjyvz97",
    "142.147.128.93:6593:amkdfvil:wrpirhjyvz97",
    "104.239.105.125:6655:amkdfvil:wrpirhjyvz97",
    "173.0.9.70:5653:amkdfvil:wrpirhjyvz97",
]

proxy_pool = []
for p in raw_proxies:
    host, port, user, pwd = p.split(":")
    proxy_url = f"http://{user}:{pwd}@{host}:{port}"
    proxy_pool.append({"http": proxy_url, "https": proxy_url})

conn = sqlite3.connect("cars.db")
cursor = conn.cursor()


cursor.execute("""
    CREATE TABLE IF NOT EXISTS cars (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        make TEXT NOT NULL,
        model TEXT,
        trim TEXT,
        miles INTEGER,
        sell_price INTEGER,
        claimed_condition TEXT,
        excellent_pred INTEGER, 
        very_good_pred INTEGER, 
        good_pred INTEGER, 
        fair_pred INTEGER,
        link TEXT,
        explanation TEXT,
        mechanical_issues BOOLEAN
    )
    """)

cursor.execute("""
    CREATE TABLE IF NOT EXISTS checked (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        link TEXT
    )
    """)

conn.commit()
conn.close()

def check_repeat(db_name, url):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("SELECT link FROM checked")
    links = [row[0] for row in cursor.fetchall()]
    conn.close()
    return url in links
    
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

def extract_cylinder_count(text):
    match = re.search(r'\d+', text)
    return int(match.group()) if match else None



count = 0
while count < 100:
    URL = f'https://sacramento.craigslist.org/search/cta?purveyor=owner#search=2~gallery~0'
    proxy  = random.choice(proxy_pool)
    headers = random.choice(header_pool)
    soup = BeautifulSoup(requests.get(URL, headers=headers, proxies=proxy).content, 'html.parser')
    time.sleep(1)
    for car in soup.find_all('li', class_= "cl-static-search-result"):
        try:
            link = car.find('a').get('href')
            count+=1
            print(f"We have now checked {count} cars")
            if check_repeat('cars.db', link):
                print('REPEAT')
                continue
            conn = sqlite3.connect("cars.db")
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO checked (link)
            VALUES (?)
            """
            ,  (link,))
            conn.commit()
            conn.close()
            print(f"Evaluating: {link}")
            proxy  = random.choice(proxy_pool)
            headers = random.choice(header_pool)
            soup = BeautifulSoup(requests.get(link, headers=headers, proxies=proxy).content, 'html.parser')
            time.sleep(1)
            title = safe_find_text(soup.find('div', class_='attr auto_title_status'), 'span', 'valu')
            if title is None or title.lower() != 'clean':
                print('NOT CLEAN TITLE')
                print(link)
                continue
            price = safe_find_text(soup, 'span', class_='price').replace('$', '').replace(',', '')

            if not price.isdigit() or int(price) > 7000:
                print('MORE THAN $7000')
                continue

            year = safe_find_text(soup.find('div', class_='attr important'), 'span', class_='valu year')
            if int(year) < 1992:
                continue
            price = int(price)

            miles = safe_find_text(soup.find('div', class_='attr auto_miles'), 'span', class_='valu').replace(',', '')
            miles = int(miles) if miles.isdigit() else 0
            


            makemodel = safe_find_text(soup.find('div', class_='attr important'), 'span', class_='valu makemodel').lower()
            
            if not any(brand in makemodel.lower() for brand in ['toyota', 'honda', 'lexus']):
                print('Not a Japanese Car')
                continue
            postingtitle = safe_find_text(soup, 'span', id_='titletextonly') 
            postingbody = safe_find_text(soup, 'section', id_='postingbody') 

            condition = safe_find_text(soup.find('div', class_='attr condition'), 'span', class_='valu')
            exterior_color = safe_find_text(soup.find('div', class_='attr auto_paint'), 'span', class_='valu')
            cylinders = safe_find_text(soup.find('div', class_='attr auto_cylinders'), 'span', class_='valu')
            cylinders = extract_cylinder_count(cylinders)
            body_type = safe_find_text(soup.find('div', class_='attr auto_bodytype'), 'span', class_='valu')
            transmission = safe_find_text(soup.find('div', class_='attr auto_transmission'), 'span', class_='valu')
            transmission = transmission.capitalize() if transmission else ''
            body_type = safe_find_text(soup.find('div', class_='attr auto_bodytype'), 'span', class_='valu')


            response = client.models.generate_content(
                model="gemini-2.0-flash",
                config=types.GenerateContentConfig(
                    system_instruction=    "Your Job is identifying car models, given a postings title, car information, as well as a postings body," \
                    "output a python tuple that is (make, model, trim, mechanical_issues). Provide the one that is most likely, if multiple are there likely" \
                    "send back the cheapest one. OUTPUT HAS TO BE A PYTHON TUPLE. MECHANICAL ISSUES IS A BOOLEAN INDICATING WORK NEEDS TO BE DONE. " \
                    "IF NO TRIM IS SPECIFIFIED SEARCH UP THE CHEAPEST TRIM FOR THAT CAR",
                    temperature=0),
                contents=[makemodel, postingtitle, postingbody]
            )
            time.sleep(4)
            make, model, trim, mechanical_issues = ast.literal_eval(response.text.strip('`').strip('python').replace('\n', ""))
            print(f"The car is most likely a {make}, {model}, {trim}")
            payload = {
                "api_key": "REVHzhANOzlKNPFu755EGgfbkpqj0mzN",
                "car_type": "used",
                "year": year,
                "make": make,
                "model": model,
                "trim": trim,
                "miles": miles,
                "base_exterior_color": exterior_color,
                "latitude": 38.581573,
                "longitude": -121.494400,
                "transmission": transmission,
                "cylinders": cylinders,
                "condition" : condition
            }

            json_dump = json.dumps(payload)

            response = client.models.generate_content(
                model="gemini-2.0-flash",
                config=types.GenerateContentConfig(
                    system_instruction=    
                    "You are an expert used car price analyzer. Given specs of a car, provide an estimate for if the car is fair, good, very good, and excellent" \
                    "based on th kelly blue book definitions for each"
                    "car, if sold in Sacramento, California, 95834, on June 30th 2025"
                    "PLACE EMPHASIS ON THE CONDITION OF THE CAR"
                    "CHECK WITH KELLY BLUE BOOK"
                    "YOUR OUTPUT HAS TO BE A JSON FILE CONTAINING THE VALUE OF EACH AND THEN AN EXPLANATION SO ONLY 5 VALUES"
                    "{excellent_value : ..., very_good_value : ... good_value : ... , fair_value : ..., explanation: ...}",
                    temperature=0),
                contents=[json_dump]
            )
            time.sleep(4)
            cleaned = ast.literal_eval(response.text.strip('`').strip('json').replace('\n', ''))
            print(cleaned)
            conn = sqlite3.connect("cars.db")
            cursor = conn.cursor()

            cursor.execute("""
            INSERT INTO cars (make, model, trim, miles, sell_price, claimed_condition, excellent_pred, very_good_pred, good_pred, fair_pred, link, explanation, mechanical_issues)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (payload['make'], payload['model'], payload['trim'], payload['miles'], price, payload['condition'], 
                cleaned['excellent_value'], cleaned['very_good_value'], cleaned['good_value'], cleaned['fair_value'], link, cleaned['explanation'], mechanical_issues))

            conn.commit()

            conn.close()
            print("ADDED TO DATABASE")
        except Exception as e:
            print(f"An error occurred: {e}")