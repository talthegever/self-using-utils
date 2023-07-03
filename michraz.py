
# -*- coding: utf-8 -*-
from selenium import webdriver
import chromedriver_binary  # Adds chromedriver binary to path
import time
import requests

PAGE = r"https://apps.land.gov.il/MichrazimSite/#/michraz/20220017"
TOKEN = "5858305457:AAH51jDbYaCZZl4MYmy89XYG8SLSrPxz11I"
CHAT_ID = "-1001780410833"

driver = webdriver.Chrome()
driver.get(PAGE)
time.sleep(10)
while driver.page_source.find("סטטוס") == -1
    driver.get(PAGE)
    time.sleep(10)
if driver.page_source[driver.page_source.find("סטטוס"):driver.page_source.find("סטטוס")+120] !='סטטוס: </span><span class="status status-description" tabindex="0" aria-label="סטטוס טרם הוכרזו זוכים">טרם הוכרזו זוכים<':
    requests.get(f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={CHAT_ID}&text=something changed!\n{PAGE.split('#')[0]}%23{PAGE.split('#')[-1]}\n")
driver.close()
