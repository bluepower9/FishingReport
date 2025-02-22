from fastapi import FastAPI
import uvicorn
import datetime

app = FastAPI()

@app.get(path='/test')
def test():
    return {'alive': True}


@app.get(path='/counts')
def get_counts(start:str, end: str = datetime.datetime.today()):

    pass



if __name__ == '__main__':
    uvicorn.run('main:app', host='127.0.0.1', port=1234, reload=True)