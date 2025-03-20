import datetime
import sqlite3
from data.FishCountsDB import FishCountsDB


def get_fish_list():
    sql = 'SELECT fish FROM fish ORDER BY fish'
    db = FishCountsDB()

    with db.db as conn:
        cur = conn.cursor()
        res = cur.execute(sql)
    
    return [x[0] for x in res.fetchall()]


def get_ports_list():
    sql = 'SELECT port FROM ports ORDER BY port'
    db = FishCountsDB()

    with db.db as conn:
        cur = conn.cursor()
        res = cur.execute(sql)
    
    return [x[0] for x in res.fetchall()]


def get_boats_list():
    sql = 'SELECT boat FROM boats ORDER BY boat'
    db = FishCountsDB()

    with db.db as conn:
        cur = conn.cursor()
        res = cur.execute(sql)
    
    return [x[0] for x in res.fetchall()]
    



def list_fishing_item(item: str):
    '''
    Gets a list of all fishing items for requested type. Must be: ports, boats, fish
    
    :param item: string, must be ports, boats, fish
    '''
    assert item in ['ports', 'boats', 'fish']

    sql = f'SELECT * FROM {item}'
    db = FishCountsDB()

    with db.db as conn:
        cur = conn.cursor()
        cur.execute(sql)
        res = cur.fetchall()

    return res


def get_filters_sql(table, filters) -> str:
    '''
    Processes filters and converts them into a SQL statement.
    '''
    # table name : column name
    tablekeys = {
        'fish': 'fish',
        'boats': 'boat', 
        'ports': 'port'
    }

    if filters is None or len(filters) == 0:
        return ''

    filterstr = ', '.join([(f"'{fi}'") for fi in filters])

    # only 1 filter item so different operator
    tablesql = f'{table}.{tablekeys[table]}'
    if len(filters) == 1:
        return f'AND {tablesql}={filterstr}'

    else:
        return f'AND {tablesql} IN ({filterstr})'




def aggregate_fish_range(start:datetime.datetime, end: datetime.datetime, item: str=None, filters={}):
    # fish counts

    db = FishCountsDB(file='./data/fishcountsdb.db')
    conn = db.db
    cur = conn.cursor()

    # converts filters into SQL statements
    filtersql = ''
    for filter, data in filters.items():
        filtersql += get_filters_sql(filter, data)


    # boatsql = f'''
    # SELECT date, boats.boat, fish.fish, boats.boat, ports.port, SUM(count) FROM trips 
    #     JOIN counts ON trips.id = counts.trip_id
    #     JOIN fish ON counts.fish = fish.id
    #     JOIN boats ON trips.boat = boats.id
    #     WHERE date >= ? AND date <= ? {filtersql}

    #     GROUP BY date, fish.fish
    #     '''


    fishsql = f'''
    SELECT date, fish.fish, SUM(count), SUM(trips.anglers) FROM trips 
        JOIN counts ON trips.id = counts.trip_id
        JOIN fish ON counts.fish = fish.id
        JOIN boats ON trips.boat = boats.id
        JOIN ports ON trips.port = ports.id
        WHERE date >= ? AND date <= ? {filtersql}

        GROUP BY date, fish.fish
        '''
    
    print(fishsql)

    res = cur.execute(fishsql, (start, end))
    labels = ['date', 'fish', 'count', 'anglers']
    data = map(lambda d: {'date': d[0], 'fish': d[1], 'count': d[2], 'anglers': d[3]},res.fetchall())

    return list(data)
