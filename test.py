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

gemini_api   = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=gemini_api)

explanation_1 = """Based on Kelly Blue Book standards for a 2003 Toyota 4Runner SR5 with 199,000 miles in Sacramento, CA (95834) as of July 2, 2025, the estimated values are as follows:

*   **Excellent:** This car is in top condition. It looks new and is mechanically sound. It has complete and verifiable service records. Expect only minor cosmetic defects and essentially no mechanical issues. This car would be valued around $7500.

*   **Very Good:** This car is clean and well-maintained. It has minor cosmetic defects (e.g., small scratches or dings) and may have some minor mechanical issues that are easily addressed. It has some service records. This car would be valued around $6900.

*   **Good:** This car has some cosmetic defects (e.g., scratches, dings, or worn upholstery) and may have some mechanical issues that need attention. It may be missing some service records. Given the 'good' condition specified in the input, this car would be valued around $6300.

*   **Fair:** This car has significant cosmetic defects (e.g., rust, dents, or torn upholstery) and/or significant mechanical issues that need repair. It may be missing most or all service records. This car would be valued around $5700."""

links_lst = ['https://sacramento.craigslist.org/cto/d/rancho-cordova-2003-toyota-runner-sr5/7862889155.html', 'https://sacramento.craigslist.org/cto/d/sacramento-2008-toyota-camry/7862881066.html']
new_car = Car(
            make='Toyota',
            model='4Runner',
            trim='SR5',
            miles=199000,
            sell_price=6800,
            year=2003,
            claimed_condition='good',
            excellent_pred=7500,
            very_good_pred=6900,
            good_pred=6300,
            fair_pred=5700,
            link='https://sacramento.craigslist.org/cto/d/rancho-cordova-2003-toyota-runner-sr5/7862889155.html',
            explanation=explanation_1,
            mechanical_issues=False,
            posted_date = '2025-07-02 20:27:00'
            )
new_car_2 = Car(
            make='Toyota',
            model='camry',
            trim='base',
            miles=144000,
            sell_price=1000,
            year=2008,
            claimed_condition=None,
            excellent_pred=6443,
            very_good_pred=5818,
            good_pred=5105,
            fair_pred=4317,
            link='https://sacramento.craigslist.org/cto/d/sacramento-2008-toyota-camry/7862881066.html',
            explanation=explanation_1,
            mechanical_issues=True,
            posted_date = '2025-07-02 19:19:00'
            )



print(response.text)

logging.info(f"WE SEARCHED THROUGH 50 DIFFERENT CARS AND ARE NOW DONE")
msg = EmailMessage()

msg['Subject'] = 'Automatic Email from Craigslist Scraper'
msg['From'] = os.getenv('EMAIL_USERNAME')
msg['To'] = 'jevanchahal1@gmail.com'#, 'ramanchhokar@gmail.com', 'ss.chhokar@gmail.com'
msg.set_content(response.text)

with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
    smtp.login(os.getenv('EMAIL_USERNAME'), os.getenv('EMAIL_PASSWORD'))
    smtp.send_message(msg)