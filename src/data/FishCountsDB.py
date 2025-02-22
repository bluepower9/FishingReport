import sqlite3


class FishCountsDB:
    def __init__(self, file='./data/fishcountsdb.db'):
        self.file = file
        self.__db = None


    def connect_db(self):
        self.__db = sqlite3.connect(self.file)
        return self.__db

    @property
    def db(self):
        if not self.__db:
            return self.connect_db()

        return self.__db