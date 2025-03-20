from bs4 import BeautifulSoup
from collections import defaultdict
from data.FishCountsDB import FishCountsDB
from fractions import Fraction
import requests
import datetime
import re
import csv
import sqlite3
import inflect


class Scraper976:
    def __init__(self, dbpath='./data/fishcounts.db'):
        self.dbpath = dbpath
        self.db = FishCountsDB(file=dbpath)

    
    def get_id(self, name, table):
        # conn = self.db.db
        
        sqlcols ={ 
            'fish': ['fish', 'fish'],
            'ports': ['ports', 'port'],
            'boats': ['boats', 'boat']
        }

        if table not in sqlcols.keys():
            return None

        with self.db.db as conn:
            cur = conn.cursor()
            table, namecol = sqlcols[table]
            selectsql = f'SELECT id from {table} WHERE {namecol} = ?'
            res = cur.execute(selectsql, (name, ))

            resid = res.fetchone()

            # adds to table if it doesn't exist
            if resid == None:
                insertsql = f'INSERT INTO {table}({namecol}) VALUES(?)'
                res = cur.execute(insertsql, (name, ))
                resid = cur.lastrowid
                conn.commit()

                return resid
            
            else:
                return resid[0]



    def save_data(self, date, data):
        '''
        Writes data to sqlite db.
        
        :param data: data to save. format: (date (anglers, {fish: count}))
        '''
        print('Saving data for ', date)
        # db = FishCountsDB(self.dbpath)
        # db = self.db
        # conn = db.db

        with self.db.db as conn:
            cur = conn.cursor()
            for port, boats in data.items():
                for boat, trips in boats.items():
                    for t in trips:

                        boatid = self.get_id(boat, 'boats')
                        portid = self.get_id(port, 'ports')

                        tripsql = 'INSERT INTO trips(date, anglers, boat, port, days) VALUES(?, ?, ?, ?, ?)'
                        cur.execute(tripsql, (date, t['anglers'], boatid, portid, t['days']))
                        tripid = cur.lastrowid

                        counts = t['counts']
                        for fish, count in counts.items():
                            fishid = self.get_id(fish, 'fish')
                            countsql = 'INSERT INTO counts(trip_id, fish, count) VALUES(?, ?, ?)'
                            cur.execute(countsql, (tripid, fishid, count))

            conn.commit()

            
    
    def get_day_totals(self, month, day, year) -> dict:
        '''
        Gets totals for given day of fish caught.
        Returns a dict of fish:count 
        '''

        #validates date given
        date = datetime.datetime(year=year, month=month, day=day)
        today = datetime.date.today()

        if date.date() > today:
            raise ValueError('Date is in the future.')
        
        url = f"https://www.976-tuna.com/counts?m={month}&d={day}&y={year}"

        data = requests.get(url)
        totals = self.parse_html(date, data.text)
    
        return datetime.date(month=month, day=day, year=year), totals


    def parse_port(self, counttext:BeautifulSoup) -> tuple:
        '''
        Parses the port name and gets a link to the port that can be used to further parse boat stats.
        
        :param counttext: BeautifulSoup object that can be used to find the parent elements.

        :return (port, link):
        '''

        base_url = 'https://www.976-tuna.com'
        parent = counttext.parent.parent
        port = parent.find('b').find('a')
        # print(port.get_text())
        # print(base_url + port['href'])

        return port.get_text(), base_url+port['href']


    def aggregate_fish_count(self, counts:list) -> dict:
        '''
        Aggregates a list of fish counts to single totals and converts data into dict format.
        '''
        totals = defaultdict(int)
        for c in counts:
            splitdata = c.split()
            count, fish = int(splitdata[0]), ' '.join(splitdata[1:])
            totals[fish.lower()] += count

        return totals
    

    def parse_boat_trips(self, html:BeautifulSoup) -> dict:
        '''
        Parses boat trips found in port counts page. Takes in html for one section which represents all trips for a boat on a given day.
        '''
        stats = html.find('a')
        text = ''

        # gets full text for the day of the boat's html stats
        while stats and 'Reports' not in stats.text:
            text += stats.text
            stats = stats.nextSibling

        # print(text)
            
        trips = text.split('The')   # splits text into 2 sections, 1 for each trip.
        tripstats = []
        # parses trip information for each individual trip
        for t in trips:
            totals = {}

            # days = t.split('Day')[-2].split()[-1].strip('-')
            days = '1'
            days_split = t.split('Day')
            if len(days_split) > 1:
                days = days_split[-2].split()[-1].strip('-')

            if 'Day' not in t or days in ['Full', 'Lobster']:
                days ='1'

            # adds days to the totals. If an exception is thrown, number of days is not a number or Full and defaults to 1.
            try:
                totals['days'] = float(Fraction(days))
            except Exception as e:
                print('Exception: ', e, '\nNo day count found.', '\ntext:\t ', text)
                totals['days'] = float(1)

            totals['anglers'] = int(t.split('angler')[0].strip().split()[-1].strip())
            
            caught = t.strip().split('caught')[1].split(',')
            counts = [c.strip().strip('.').removeprefix('and').removesuffix('released').strip() for c in caught]
            totals['counts'] = self.aggregate_fish_count(counts)

            tripstats.append(totals)

        # print('\n', tripstats)
        return tripstats



    def parse_boats(self, date:datetime.datetime, port:str, url:str) -> dict:
        '''
        Parses the boat totals of fish caught and returns dict of information.
        
        :param date: date to search for
        :param port: port name
        :param url: url to port

        :return dict:
        {
            boatname: {
                trips: [{stats}]
            }            
        }
        '''
        data = requests.get(url)
        soup = BeautifulSoup(data.text, 'html.parser')
        inf = inflect.engine()
        date_format = date.strftime(f'%a %B {inf.ordinal(date.day)}')

        start = soup.find(string=re.compile(date_format))
        if start is None:
            print(f'no date found for {port}. date: {date_format}')
            return {}
        
        start = start.parent        
        sib = start.find_next_sibling()

        boats = {}
        #iterates through each boat
        while sib and sib.name == 'div': 
            counts = sib.find('h5')
            boat_stats = self.parse_boat_trips(counts)
            boat = counts.find('a').text
            boats[boat] = boat_stats 
            
            sib = sib.find_next_sibling()

        # print(boats)
        return boats  
        


    def parse_html(self, date:datetime.datetime, html:str) -> dict:
        '''
        Parses the html data and retrieves fish totals.
        '''
        totals = defaultdict(int)
        soup = BeautifulSoup(html, 'html.parser')
        trips = soup.findAll(string=re.compile(r'Total Fish -'))

        # no fish reported for that day
        if len(trips) == 0:
            return {}
        
        portinfo = self.parse_port(trips[0])
        self.parse_boats(date, portinfo[0], portinfo[1])
        
        data = {}

        for t in trips:
            portinfo = self.parse_port(t)
            port_stats = self.parse_boats(date, portinfo[0], portinfo[1])
            data[portinfo[0]] = port_stats

        # print(data) 
        return data
        

def scrape_date_range(start:datetime.datetime, end:datetime.datetime):
    scraper = Scraper976(dbpath='./data/newfishingdb.db')
    while start <= end:
        date, data = scraper.get_day_totals(start.month, start.day, start.year)
        scraper.save_data(date, data)

        start += datetime.timedelta(days=1)



if __name__ == '__main__':
    start = datetime.datetime(month=1, day=1, year=2024)
    end = datetime.datetime.today() - datetime.timedelta(days=1)
    # scrape_date_range(start, end)
