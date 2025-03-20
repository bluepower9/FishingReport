from pydantic import BaseModel
import datetime
from fastapi import Form
from typing import Annotated

class DateRangeRequest(BaseModel):
    start: datetime.date
    end: datetime.date = datetime.date.today()
    fish: list = None
    boats: list = None
    ports: list= None


class DateRangeFish(DateRangeRequest):
    fish: str
    

