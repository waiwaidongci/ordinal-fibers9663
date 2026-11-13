from pydantic import BaseModel,Field,ConfigDict
class ReadingInput(BaseModel):
    study_id:int
    treatment_id:int
    specimen_code:str=Field(min_length=2,max_length=60,pattern=r'^[A-Za-z0-9_-]+$')
    grade:int=Field(ge=1,le=9,strict=True)
    source_note:str=Field(default='',max_length=250)
class ReadingOut(ReadingInput):
    grade:float
    id:int
    model_config=ConfigDict(from_attributes=True)
