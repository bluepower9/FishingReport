from pydantic import BaseModel
import datetime

class DateRangeRequest(BaseModel):
    start:str
    end:str = str(datetime.datetime.today())
    fish:list = []
    boats:list = []
    ports:list = []


class DateRangeFish(DateRangeRequest):
    fish: str
    

