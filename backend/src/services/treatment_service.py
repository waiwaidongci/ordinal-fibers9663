from sqlalchemy import select,func
from fastapi import HTTPException
from src.models import Treatment
from src.services.study_service import get_study

def list_treatments(db,study_id):return db.scalars(select(Treatment).where(Treatment.study_id==study_id).order_by(Treatment.code)).all()
def save(db,data,id=None):
    get_study(db,data.study_id)
    if db.scalar(select(Treatment).where(Treatment.study_id==data.study_id,Treatment.code==data.code,Treatment.id!=(id or 0))):raise HTTPException(409,'工艺编号重复')
    t=db.get(Treatment,id) if id else Treatment()
    if id and not t:raise HTTPException(404,'工艺不存在')
    if id and t.study_id!=data.study_id:raise HTTPException(422,'不能迁移工艺所属研究')
    if not id and db.scalar(select(func.count()).select_from(Treatment).where(Treatment.study_id==data.study_id))>=5:raise HTTPException(422,'每研究最多5个预定义工艺')
    for k,v in data.model_dump().items():setattr(t,k,v)
    db.add(t);db.commit();return t

def create_treatment(db,data):return save(db,data)
def update_treatment(db,id,data):return save(db,data,id)
