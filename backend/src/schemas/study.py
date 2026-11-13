from pydantic import BaseModel,Field,ConfigDict
class StudyInput(BaseModel):
    code:str=Field(min_length=2,max_length=40,pattern=r'^[A-Za-z0-9_-]+$')
    name:str=Field(min_length=2,max_length=140)
    protocol:str=Field(default='',max_length=1200)
    source_file:str=Field(default='',max_length=140)
class StudyOut(StudyInput):
    id:int
    model_config=ConfigDict(from_attributes=True)
