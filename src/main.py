from fastapi import FastAPI, Form, Depends
from fastapi.middleware.cors import CORSMiddleware
from util.util import aggregate_fish_range, get_fish_list, get_ports_list, get_boats_list
from models.RequestModels import DateRangeRequest
from typing import Annotated, List
import uvicorn
import datetime

app = FastAPI()

origins = ['*']
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
    )

@app.get(path='/test')
def test():
    return {'alive': True}


@app.get(path='/filterslist')
def filters_list():
    
    return {'fish': get_fish_list(), 'ports': get_ports_list(), 'boats': get_boats_list()}


@app.post(path='/counts2')
def get_counts2(payload: DateRangeRequest):
    filters = {
        'fish': payload.fish,
        'boats': payload.boats,
        'ports': payload.ports
    }

    data = aggregate_fish_range(payload.start, payload.end, filters=filters)

    return {'length': len(data), 'data': data}


@app.get(path='/counts')
def get_counts(start:datetime.date, end: str = datetime.date.today()):

    res = aggregate_fish_range(start, end)
    
    data = res.fetchall()


    return {'length': len(data), 'data': data}
    



if __name__ == '__main__':
    uvicorn.run('main:app', host='127.0.0.1', port=1234, reload=True)