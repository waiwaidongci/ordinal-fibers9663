from sqlalchemy import select,func
from fastapi import HTTPException
from src.models import Treatment,GradeReading

def list_readings(db,study_id):return db.scalars(select(GradeReading).where(GradeReading.study_id==study_id).order_by(GradeReading.specimen_code)).all()
def save(db,data,id=None):
    t=db.get(Treatment,data.treatment_id)
    if not t or t.study_id!=data.study_id:raise HTTPException(422,'读数工艺须属于当前研究')
    if db.scalar(select(GradeReading).where(GradeReading.study_id==data.study_id,GradeReading.specimen_code==data.specimen_code,GradeReading.id!=(id or 0))):raise HTTPException(409,'独立试样编号重复；不能重复计入')
    row=db.get(GradeReading,id) if id else GradeReading()
    if id and not row:raise HTTPException(404,'等级记录不存在')
    if id and row.study_id!=data.study_id:raise HTTPException(422,'不能迁移试样所属研究')
    if not id and db.scalar(select(func.count()).select_from(GradeReading).where(GradeReading.study_id==data.study_id))>=2000:raise HTTPException(422,'每研究最多2000份试样')
    for k,v in data.model_dump().items():setattr(row,k,v)
    db.add(row);db.commit();return row

def create_reading(db,data):return save(db,data)
def update_reading(db,id,data):return save(db,data,id)
