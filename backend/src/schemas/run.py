from pydantic import BaseModel,Field,ConfigDict
from datetime import datetime
class RunInput(BaseModel):
    name:str=Field(min_length=2,max_length=140)
    study_id:int
    alpha:float=Field(default=.05,gt=0,lt=1,allow_inf_nan=False,strict=True)
    bootstrap_seed:int=Field(default=20261113,ge=0,le=2**32-1,strict=True)
    bootstrap_replicates:int=Field(default=9999,ge=100,le=100000,strict=True)
class RunOut(RunInput):
    id:int
    status:str
    snapshot:dict
    result:dict
    error:str
    created_at:datetime
    model_config=ConfigDict(from_attributes=True)
