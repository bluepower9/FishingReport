import sqlite3
import json
import datetime


def run_file(filename='dbsetup.sql', db='fishcountsdb.db'):
    conn = sqlite3.connect(db)

    with sqlite3.connect(db) as conn:
        cur = conn.cursor()
        with open(filename, 'r')  as file:
            queries = file.read().split(';')
            for q in queries:
                try: 
                    cur.execute(q)
                    # print('*'*25 + '\n' + f'Executed SQL statement: {q}')
                
                except Exception as e:
                    print(f'Failed SQL statement: {q}.  Error: {e}')
        
        conn.commit()


def change_date_format(db='fishcountsdb.db'):
    # conn = sqlite3.connect(db)

    with sqlite3.connect(db) as conn:
        cur = conn.cursor()
        rows = cur.execute('SELECT * FROM trips').fetchall()
        for trip in rows:
            cur.execute('UPDATE trips SET date=? WHERE id=?', (trip[1].split()[0], trip[0]))


        conn.commit()            
        
        

if __name__ == '__main__':
    print('SETTING UP DATABASE')
    run_file(filename='dbsetup.sql', db='fishcountsdb_copy.db')

    # change_date_format(db='fishcountsdb_copy.db')