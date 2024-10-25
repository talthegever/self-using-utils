from os.path import exists
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from time import sleep
from datetime import datetime
from requests import get


def extract_line(base_str: str, char_index: int) -> str:
    return base_str[char_index:base_str.find("\n", char_index)]


def parse_time(date: [str, datetime.date]) -> [datetime.date, str]:
    if isinstance(date, str):
        return datetime.strptime(date, '%d/%m/%Y')
    else:
        return date.strftime('%d/%m/%Y')


def get_date():
    with open(DATE_FILE, "r") as f:
        return parse_time(f.read())


def set_date(date: datetime.date):
    with open(DATE_FILE, "w") as f:
        f.write(parse_time(date))


def send_telegram_message(text: str):
    get(f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={CHAT_ID}&text={text}")


def update_date(date: datetime.date):
    send_telegram_message(f"new lottery that ends at {date}")
    set_date(date)


TOKEN = "5858305457:AAH51jDbYaCZZl4MYmy89XYG8SLSrPxz11I"
CHAT_ID = "-1001780410833"
PAGE = r"https://www.dira.moch.gov.il/ProjectsList"
DATE_FILE = "last_date.txt"

chrome_options = Options()
# chrome_options.add_argument("--headless")
driver = webdriver.Chrome(options=chrome_options)

driver.get(PAGE)
sleep(5)
MODEL = driver.page_source

line = extract_line(MODEL, MODEL.find("סיום הרשמה", MODEL.find("סיום הרשמה") + 50) + 20)
newest_date = parse_time(line[line.find(">") + 1:line.find("<")])


if exists(DATE_FILE):
    if newest_date > get_date():
        update_date(newest_date)
else:
    update_date(newest_date)
