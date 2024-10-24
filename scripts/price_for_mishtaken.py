from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from time import sleep


def extract_line(base_str: str, char_index: int):
    return base_str[char_index:base_str.find("\n", char_index)]


PAGE = r"https://www.dira.moch.gov.il/ProjectsList"

chrome_options = Options()
chrome_options.add_argument("--headless")
driver = webdriver.Chrome(options=chrome_options)

driver.get(PAGE)
sleep(5)
MODEL = driver.page_source

line = extract_line(MODEL, MODEL.find("סיום הרשמה", MODEL.find("סיום הרשמה")+30))
print(line)

