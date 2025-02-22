from Scraper976 import Scraper976
import datetime


def scrape_date_range(start:datetime.datetime, end:datetime.datetime):
    scraper = Scraper976()
    while start <= end:
        date, data = scraper.get_day_totals(start.month, start.day, start.year)
        scraper.save_data(date, data)

        start += datetime.timedelta(days=1)



if __name__ == '__main__':
    start = datetime.datetime(month=12, day=22, year=2024)
    end = datetime.datetime.today() - datetime.timedelta(days=1)
    scrape_date_range(start, end)