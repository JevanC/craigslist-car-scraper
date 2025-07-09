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

gemini_api   = os.getenv("GEMINI_API_KEY")
header_pool  = json.loads(os.getenv("HEADER_POOL_JSON", "[]"))
response = requests.get(
    os.getenv('PROXY_URL'),
    headers={"Authorization": os.getenv('PROXY_TOKEN')}
)
raw_proxies = [f"{i['proxy_address']}:{i['port']}:{i['username']}:{i['password']}" for i in response.json()['results']]



proxy_pool = []
for p in raw_proxies:
    host, port, user, pwd = p.split(":")
    proxy_url = f"http://{user}:{pwd}@{host}:{port}"
    proxy_pool.append({"http": proxy_url, "https": proxy_url})

    
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



