import time
from typing import List
import requests
import pywhatkit
from datetime import datetime

AREA = "%D7%94%D7%A9%D7%A8%D7%95%D7%9F"  # hasharon

CONDITION_GOOD_PLUS = "2"

ELECTRICITY = "1"
FURNITURE = "2"

OVEN = "10007"
BED = "20016"
SOFA = "20017"
FOOD_CORNER = "20033"

TOKEN = "5858305457:AAH51jDbYaCZZl4MYmy89XYG8SLSrPxz11I"
CHAT_ID = "-1001780410833"

CACHE_PATH = r"C:\Users\home\Desktop\טל\חחחחחחח אני חנון רצח\item_ids.txt"
LOG_PATH = r"C:\Users\home\Desktop\טל\חחחחחחח אני חנון רצח\log.txt"


def check_new_item_id_in_file(item_ids: List[str]):
    """
    extract unseen ids from list
    :return: ids list to write to cache file
    """
    with open(CACHE_PATH, "r") as my_file:
        content = my_file.read()

    return [item for item in item_ids if item not in content]


def insert_ids_to_file(item_ids: List[str]):
    """
    write new items to cache file
    :param item_ids: ids for ads
    """
    with open(CACHE_PATH, "a") as my_file:
        my_file.write(',')
        my_file.write(','.join(item_ids))


def get_last_hour_items_from_html(search_result: str) -> List[str]:
    """
    gets new item ids from request
    :param search_result: html page from url request
    :return:
    """
    relevant_items = (search_result[search_result.find("</thead>") + len("</thead>"):search_result.find("</table>")])
    relevant_items = relevant_items.split(r"""<tr class="objectsTitleTr""")

    item_ids = [item[item.find(",") + 1:item.find(")")] for item in relevant_items[1:]]

    return check_new_item_id_in_file(item_ids)


def send_urls(item_ids: List[str]):
    """
    telegram bot
    :param item_ids: for generating advertisment urls
    """
    urls = [f"https://www.agora.co.il/showPhoto.asp?id={item_id}" for item_id in item_ids]
    for url in urls:
        requests.get(f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={CHAT_ID}&text={url}")


def search_to_new_alert(search) -> int:
    """
    :param search:
    :return:
    """
    ids_to_send = get_last_hour_items_from_html(search.text)
    if ids_to_send:
        print("new: ", ids_to_send)
        send_urls(ids_to_send)
        insert_ids_to_file(ids_to_send)
        return 1
    else:
        return 0


def main():
    count: int = 0
    oven_search = requests.get(
        f'https://www.agora.co.il/toGet.asp?dealType=1&takeCity={AREA}&category={ELECTRICITY}&subcategory={OVEN}&condition={CONDITION_GOOD_PLUS}')
    count += search_to_new_alert(oven_search)

    bed_search = requests.get(
        f'https://www.agora.co.il/toGet.asp?dealType=1&takeCity={AREA}&category={FURNITURE}&subcategory={BED}&condition={CONDITION_GOOD_PLUS}')
    count += search_to_new_alert(bed_search)

    sofa_search = requests.get(
        f'https://www.agora.co.il/toGet.asp?dealType=1&takeCity={AREA}&category={FURNITURE}&subcategory={SOFA}&condition={CONDITION_GOOD_PLUS}')
    count += search_to_new_alert(sofa_search)

    table_search = requests.get(
        f'https://www.agora.co.il/toGet.asp?dealType=1&takeCity={AREA}&category={FURNITURE}&subcategory={FOOD_CORNER}&condition={CONDITION_GOOD_PLUS}')
    count += search_to_new_alert(table_search)

    if count == 0:
        print("nothing new")
        with open(LOG_PATH, "a") as log_file:
            log_file.write(f"\n nothing new on {datetime.now()}")
    else:
        with open(LOG_PATH, "a") as log_file:
            log_file.write(f"\n sent telegram items!!!")


if __name__ == '__main__':
    main()
