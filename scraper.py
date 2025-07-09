from bs4 import BeautifulSoup
import pandas as pd
import requests
from google.genai import types
import ast
from google import genai
import re
import json
import time
import random
import loadenv
import os
from dotenv import load_dotenv
from models import Checked, Car
from db import Session, init_db
from datetime import datetime
import smtplib
from email.message import EmailMessage
import logging
import sys

session = Session()
init_db()
load_dotenv()

logging.basicConfig(
    level=logging.INFO,                     
    format='%(asctime)s %(levelname)s %(message)s',  
    handlers=[
        logging.StreamHandler(sys.stdout) 
    ]
)

delay = random.randint(0,1800)
logging.info(f"Program will be delayed for {int(delay/60)} minutes to avoid detection")
#time.sleep(delay)

gemini_api   = os.getenv("GEMINI_API_KEY")
header_pool  = json.loads(os.getenv("HEADER_POOL_JSON", "[]"))
response = requests.get(
    os.getenv('PROXY_URL'),
    headers={"Authorization": os.getenv('PROXY_TOKEN')}
)
raw_proxies = [f"{i['proxy_address']}:{i['port']}:{i['username']}:{i['password']}" for i in response.json()['results']]

client = genai.Client(api_key=gemini_api)


proxy_pool = []
for p in raw_proxies:
    host, port, user, pwd = p.split(":")
    proxy_url = f"http://{user}:{pwd}@{host}:{port}"
    proxy_pool.append({"http": proxy_url, "https": proxy_url})

def delete_old_listing(session, header_pool, proxy_pool):
    proxy  = random.choice(proxy_pool)
    headers = random.choice(header_pool)

    for old_car, old_link, old_cars_make, old_cars_model in session.query(Car, Car.link, Car.make, Car.model).all():
        soup = BeautifulSoup(requests.get(old_link, headers=headers, proxies=proxy).content, 'html.parser')
        if soup.find('div', class_='removed') is not None:
            logging.info(f'{old_cars_make} {old_cars_model} LISTING EXPIRED')
            session.delete(old_car)
            session.commit()
        else:
            logging.info(f'{old_cars_make} {old_cars_model} LISTING IS STILL ACTIVE')
        time.sleep(random.uniform(15, 25))
        
delete_old_listing(session, header_pool, proxy_pool)

def refresh_session():
    global session
    session.close()
    session = Session()

def check_repeat(session, url):
    return session.query(Checked).filter_by(link=url).first() is not None

    
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
limit = 100
cars_lst = []
links_lst = []

while count < limit:
    URL = f'https://sacramento.craigslist.org/search/cta?purveyor=owner#search=2~gallery~0'
    proxy  = random.choice(proxy_pool)
    headers = random.choice(header_pool)
    soup = BeautifulSoup(requests.get(URL, headers=headers, proxies=proxy).content, 'html.parser')
    time.sleep(random.uniform(15, 25))
    for car in soup.find_all('li', class_= "cl-static-search-result"):
        try:
            link = car.find('a').get('href')
            count+=1
            logging.info(f"We have now checked {count} cars")
            if check_repeat(session, link):
                logging.info(f"CAR HAS ALREADY BEEN CHECKED")
                if count >= limit:
                    break
                continue
            new_link = Checked(link=link)
            session.add(new_link)
            session.commit()
            logging.info(f"Evaluating: {link}")
            proxy  = random.choice(proxy_pool)
            headers = random.choice(header_pool)
            soup = BeautifulSoup(requests.get(link, headers=headers, proxies=proxy).content, 'html.parser')
            time.sleep(random.uniform(15, 25))
            title = safe_find_text(soup.find('div', class_='attr auto_title_status'), 'span', 'valu')
            if title is None or title.lower() != 'clean':
                logging.info('NOT CLEAN TITLE')
                if count >= limit:
                    break
                continue
            price = safe_find_text(soup, 'span', class_='price').replace('$', '').replace(',', '')
            if not price.isdigit() or int(price) > 7000:
                logging.info("MORE THAN $7000")
                if count >= limit:
                    break
                continue

            year = safe_find_text(soup.find('div', class_='attr important'), 'span', class_='valu year')
            if int(year) < 2000:
                logging.info('CAR IS TOO OLD')
                if count >= limit:
                    break
                continue
            price = int(price)

            miles = safe_find_text(soup.find('div', class_='attr auto_miles'), 'span', class_='valu').replace(',', '')
            miles = int(miles) if miles.isdigit() else 0
            if miles > 200000:
                logging.info('CAR HAS TOO MANY MILES')
                if count >= limit:
                    break
                continue

            makemodel = safe_find_text(soup.find('div', class_='attr important'), 'span', class_='valu makemodel').lower()
            
            if not any(brand in makemodel.lower() for brand in ['toyota', 'honda', 'lexus']):
                logging.info('Not a Japanese Car')
                if count >= limit:
                    break
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
            
            dt_string = safe_find_text(soup.find('section', class_='body'), 'time', class_='date timeago')
            posted_date = datetime.strptime(dt_string, '%Y-%m-%d %H:%M')

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
            time.sleep(5)
            make, model, trim, mechanical_issues = ast.literal_eval(response.text.strip('`').strip('python').replace('\n', ""))
            logging.info(f"The car is most likely a {make}, {model}, {trim}")
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
                    f"car, if sold in Sacramento, California, 95834, on {datetime.today()}"
                    "PLACE EMPHASIS ON THE CONDITION OF THE CAR"
                    "CHECK WITH KELLY BLUE BOOK"
                    "YOUR OUTPUT HAS TO BE A JSON FILE CONTAINING THE VALUE OF EACH AND THEN AN EXPLANATION SO ONLY 5 VALUES"\
                    "EACH VALUE OUTPUT SHOULD JUST BE A NUMBER, THE EXPLANATION OUTPUT SHOULD BE YOUR THOUGHTS ON THE CAR, WHAT CONDTION YOU WOULD CLASSIFY IT AS" \
                    "WHAT YOU THINK THE VALUE IS, AND THEN ANY ADDITONAL NOTES YOU THINK I SHOULD KNOW. THE OUTPUT WILL BE A JSON FILE FORMATTED:"
                    "{excellent_value : ..., very_good_value : ... good_value : ... , fair_value : ..., explanation: ...}",
                    temperature=0),
                contents=[json_dump]
            )
            time.sleep(5)
            cleaned = ast.literal_eval(response.text.strip('`').strip('json').replace('\n', ''))
            new_car = Car(
            make=payload['make'],
            model=payload['model'],
            trim=payload['trim'],
            miles=payload['miles'],
            sell_price=price,
            year=year,
            claimed_condition=payload['condition'],
            excellent_pred=cleaned['excellent_value'],
            very_good_pred=cleaned['very_good_value'],
            good_pred=cleaned['good_value'],
            fair_pred=cleaned['fair_value'],
            link=link,
            explanation=cleaned['explanation'],
            mechanical_issues=mechanical_issues,
            posted_date = posted_date
            )
            session.add(new_car)
            session.commit()
            cars_lst.append(new_car.to_dict())
            links_lst.append(link)
            logging.info("ADDED TO DATABASE")
        except Exception as e:
            logging.error(f"An error occurred: {e}")
            session.rollback()
            refresh_session()

response = client.models.generate_content(
    model="gemini-2.0-flash",
    config=types.GenerateContentConfig(
        system_instruction="You are an expert in sending emails. You are at the tail end of a program that evaluates craigslist listings and tries to find cars of "
        "value. You will be sending this email to me, twice a day, to let me know that the program has finished running and a list of links to the cars that wre found" \
        "Be sure to include a link https://docs.google.com/spreadsheets/d/1EFp7_gM1ezfr6yYsEkQOAOvxkLO25wzOZcPDJkok7Lg/edit?gid=1837168154#gid=1837168154 which is the google sheets" \
        "to our entire database. ALSO USE THE PROVIDED LIST OF COROSPONDING CAR VARIABLES TO HIGHLIGHT WHCIH CARS SHOULD BE FOCUSED ON. ONLY OUTPUT WHAT THE BODY OF THE EMAIL IS. NO SUBJECT LINE"
        "DO NOT OPEN THE LINKS YOURSELF. ALL PRICE ESTIMATES WERE CREATED BY WHAT GEMINI THOUGHT KBB WOULD SAY. USE YOUR OWN LOGIC IF YOU THINK GEMINI MIGHT BE OFF. MENTION HOW MANY CARS WERE SEARCHED THROUGH" \
        "MENTION PREDICTED PRICE AND SAY IT IS FROM YOU",
        temperature=0.0
    ),
    contents=[f"""
        We have looked through {count} different listings and have found the following information.

        Links to the cars:
        {chr(10).join(links_lst)}

        Car details:
        {json.dumps(cars_lst, indent=2)}
        """]
        )

logging.info(f"WE SEARCHED THROUGH {count} DIFFERENT CARS AND ARE NOW DONE")

send_email = False

if send_email:
    msg = EmailMessage()

    msg['Subject'] = 'Automatic Email from Craigslist Scraper'
    msg['From'] = os.getenv('EMAIL_USERNAME')
    msg['To'] = 'jevanchahal1@gmail.com', 'ramanchhokar@gmail.com', 'ss.chhokar@gmail.com'
    msg.set_content(response.text)
    
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(os.getenv('EMAIL_USERNAME'), os.getenv('EMAIL_PASSWORD'))
        smtp.send_message(msg)
    
    logging.info("Email sent!")
session.close()
