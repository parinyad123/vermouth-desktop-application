from fastapi import FastAPI
import uvicorn 
from pydantic import BaseModel

import torch

path = "/home/mmgs/WindowsVermouth/App/models/model/model_auto_m1_trxa_1d.pt"
modelpt = torch.load(path)

app = FastAPI()

# post
# class model_data(BaseModel):

    # algorithm_name = str,
    # algorithm_address = str
    # epoch = int
    # state_dict = dict,
    # optimizer = dict,
    # input = int,
    # tm_name = str
    # freq = str
    # feature_table = str,
    # anomaly_result_table = str,
    # model_address = str,

    # train_startpoint = int,
    # train_endpoint = int,
    # train_startdate= datetime.,
    # 'train_enddate': settings.train_enddate,

    # 'model_name': settings.model_name,
    # 'transform_method' : [settings.transform_method, [settings.min_value, settings.max_value]],
    # 'ewma_params': [settings.ewma_mean, settings.ewma_std],
    # 'anomaly_level' : settings.selectanomaly_list,
    # 'anomaly_value' : settings.selectanomaly_lelvel,
    # 'create_date' : settings.nowdate
model_buffer = []
class Model(BaseModel):
    model: dict

@app.get('/getmodel/{modelname}')
async def index(modelname: str):
    
    # model = [[12,34,56,78,0],[34,567,3,2]]
    model = modelpt
    data = {
        'model_name': modelname,
        'model' : model
    }
    return data

@app.post('/postmodel')
async def postmodel(model: Model):
    model_buffer.append(model.dict())


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=80, debug=True)