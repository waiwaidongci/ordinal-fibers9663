from pydantic import BaseModel,Field,ConfigDict
class TreatmentInput(BaseModel):
    study_id:int
    code:str=Field(min_length=2,max_length=40,pattern=r'^[A-Za-z0-9_-]+$')
    name:str=Field(min_length=2,max_length=100)
    process_note:str=Field(default='',max_length=1000)
class TreatmentOut(TreatmentInput):
    id:int
    model_config=ConfigDict(from_attributes=True)
