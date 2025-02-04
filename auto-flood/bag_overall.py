from datetime import date, timedelta
from typing import List
from pymaya.maya import Maya

maya = Maya()

PAPERS_MAYA = {"SPY": "1183441", "NASDAQ": "1186063", "STOXX": "1185172", "DJ": "1146448", "RUSS": "1206895",
               "TA90": "1209444", "NIKKEI": "1150531", "MSCI": "1185164"}


class FetchError(Exception):
    pass


class Paper:
    @staticmethod
    def get_specific_day_price(name: str, day: date):
        count = 0
        while count < 10:
            try:
                return [day_data for day_data in maya.get_price_history(PAPERS_MAYA[name], from_data=day, to_date=day)][0][
                    'CloseRate']
            except IndexError:
                day = day - timedelta(days=1)
                count += 1
        raise FetchError(f"failes to fetch price for {name} on {day}")

    def __init__(self, name: str, identifier: str, bag_percentage: float, start: date, end: date):
        self.name: str = name
        self.identifier = identifier
        self.bag_percentage = bag_percentage
        self.start_price = self.get_specific_day_price(self.name, start)
        self.end_price = self.get_specific_day_price(self.name, end)

    def __str__(self):
        return f"{self.name}: {self.start_price}->{self.end_price}"

    def profit_percentage(self):
        return (self.end_price - self.start_price) / self.start_price


class Bag:
    def __init__(self, starting_price: int, papers: List[Paper], start_date: date, end_date: date):
        self.starting_price = starting_price
        self.papers = papers.copy()
        self.start_date = start_date
        self.end_date = end_date

    def __str__(self):
        return f"total: {self.starting_price}\n------------------\n{'\n'.join([paper.name + ':' + str(paper.bag_percentage) for paper in self.papers])}\n"

    def summary(self):
        bag_total_end, bag_total_start = 0, 0

        for paper in self.papers:
            paper_old_value = self.starting_price * (paper.bag_percentage / 100)
            paper_new_value = (paper.profit_percentage() + 1) * paper_old_value
            print(paper.name, ": ", round(paper_new_value))
            bag_total_start += paper_old_value
            bag_total_end += paper_new_value

        print("started with: ", bag_total_start)
        print("ended with: ", bag_total_end)


starting_price = 115000
start_date = date(2024, 1, 1)
end_date = date.today()
SPY = Paper("SPY", "1183441", 14, start_date, end_date)
NASDAQ = Paper("NASDAQ", "1186063", 15, start_date, end_date)
STOXX = Paper("STOXX", "1185172", 29.5, start_date, end_date)
DJ = Paper("DJ", "1146448", 7, start_date, end_date)
#RUSS = Paper("RUSS", "1206895", 5.5, start_date, end_date)
#TA90 = Paper("TA90", "1209444", 5, start_date, end_date)
NIKKEI = Paper("NIKKEI", "1150531", 5, start_date, end_date)
MSCI = Paper("MSCI", "1185164", 15, start_date, end_date)
our_bag = Bag(starting_price, [SPY, NASDAQ, STOXX, DJ,
                               #RUSS, TA90,
                               NIKKEI, MSCI], start_date, end_date)
our_bag.summary()
