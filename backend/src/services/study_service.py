from sqlalchemy import select
from fastapi import HTTPException
from src.models import GradeStudy

def list_studies(db):return db.scalars(select(GradeStudy).order_by(GradeStudy.id)).all()
def get_study(db,id):
    s=db.get(GradeStudy,id)
    if not s:raise HTTPException(404,'等级研究不存在')
    return s

def save(db,data,id=None):
    if db.scalar(select(GradeStudy).where(GradeStudy.code==data.code,GradeStudy.id!=(id or 0))):raise HTTPException(409,'研究编号重复')
    s=get_study(db,id) if id else GradeStudy()
    for k,v in data.model_dump().items():setattr(s,k,v)
    db.add(s);db.commit();return s

def create_study(db,data):return save(db,data)
def update_study(db,id,data):return save(db,data,id)
