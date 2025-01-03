from datetime import datetime, date, timedelta


class DateUtils:

    @staticmethod
    def str_day_to_date(day: str) -> datetime.date:
        """
        :param day: "2023-09-15" like format
        :return: datetime of this day
        """
        return date.fromisoformat(day)

    @staticmethod
    def get_closest_valid_date(specific_date: date) -> datetime.date:
        """
        :param specific_date: datetime.date
        :return: itself. if sunday or saturday, returns last friday
        """
        while specific_date.weekday() > 4:
            specific_date = specific_date - timedelta(days=1)
        return specific_date

    @staticmethod
    def get_previous_valid_date(specific_date: date) -> datetime.date:
        """
        :param specific_date: datetime.date
        :return: yesterday. if sunday or saturday, return last Thursday
        """
        return DateUtils.get_closest_valid_date(specific_date - timedelta(days=1))

    @staticmethod
    def is_stocks_day(specific_date: datetime.date) -> bool:
        return specific_date.weekday() <= 4

    @staticmethod
    def get_date_x_days_back_from_now(days: int) -> datetime.date:
        """
        :param days: days back
        :return: datetime.date - wanted date
        """
        return date.today() - timedelta(days=days)

    @staticmethod
    def get_first_day_of_year(year: datetime.year):
        return datetime(year, 1, 1)

    @staticmethod
    def get_first_day_of_month(month: datetime.month, year: datetime.year = datetime.now().year):
        return datetime(year, month, 1)


class PrintUtils:
    ENTRY = "******************\n"

    @staticmethod
    def note_me_print(sentence: str) -> None:
        print(PrintUtils.ENTRY + sentence + PrintUtils.ENTRY)
