from scraper.Scraper976 import Scraper976
import datetime
import time


def scrape_date_range(start:datetime.date, end:datetime.date, db='./data/fishcountsdb.db'):
    scraper = Scraper976(dbpath=db)
    while start <= end:
        date, data = scraper.get_day_totals(start.month, start.day, start.year)
        scraper.save_data(date, data)

        start += datetime.timedelta(days=1)


def scrape_daily(initialrun=False):
    '''
    Scrapes fish data at 10 am daily. 

    :param initialrun: Runs once when start if True.
    '''
    today = datetime.datetime.today()
    target = today.replace(hour=10, minute=0, second=0)

    if initialrun and target > today:
        target -= datetime.timedelta(days=1)

    if not initialrun and target < today:
        target += datetime.timedelta(days=1)
    
    scraper = Scraper976()

    while True:
        now = datetime.datetime.today()
        if now > target:
            print('Scraping data for', now.date())
            date, data = scraper.get_day_totals(now.month, now.day, now.year)
            scraper.save_data(date, data)
        
            target += datetime.timedelta(days=1)
        
        time.sleep(60)



if __name__ == '__main__':
    start = datetime.date(month=3, day=6, year=2025)
    end = datetime.date.today() - datetime.timedelta(days=1)
    # scrape_date_range(start, end, db='./data/fishcountsdb.db')

    # scraper = Scraper976(dbpath='./data/fishcountsdb_copy.db')

    # id = scraper.get_id('fake tuna', 'fish')
    # print(id)

    scrape_daily()