import json
from pathlib import Path
from sqlalchemy import select,func
from fastapi import HTTPException
from redis import Redis
from src.config.settings import REDIS_URL
from src.models import RankTestRun
from src.services.study_service import get_study
from src.services.treatment_service import list_treatments
from src.services.reading_service import list_readings
from src.services.rank_inference import analyze_study
from src.constants.enums import RunStatus
redis=Redis.from_url(REDIS_URL)
def list_runs(db):return db.scalars(select(RankTestRun).order_by(RankTestRun.id.desc())).all()
def get_run(db,id):
    r=db.get(RankTestRun,id)
    if not r:raise HTTPException(404,'秩检验任务不存在')
    return r

def create_run(db,data):
    s=get_study(db,data.study_id)
    if db.scalar(select(RankTestRun).where(RankTestRun.name==data.name)):raise HTTPException(409,'任务名称重复')
    if db.scalar(select(func.count()).select_from(RankTestRun).where(RankTestRun.status.in_(['queued','running'])))>=3:raise HTTPException(429,'已有3项活动任务，请等待')
    snapshot={'study':{k:getattr(s,k) for k in ('id','code','name','protocol','source_file')},'treatments':[{k:getattr(t,k) for k in ('id','code','name','process_note')} for t in list_treatments(db,s.id)],'readings':[{k:getattr(r,k) for k in ('id','specimen_code','treatment_id','grade','source_note')} for r in list_readings(db,s.id)]}
    r=RankTestRun(**data.model_dump(),status=RunStatus.QUEUED,snapshot=snapshot);db.add(r);db.commit()
    try:redis.lpush('ordinal:runs',str(r.id))
    except Exception:pass
    return r

def execute_run(db,id):
    r=get_run(db,id)
    if r.status not in (RunStatus.QUEUED,RunStatus.RUNNING):return
    r.status=RunStatus.RUNNING;db.commit()
    try:
        result=analyze_study(r.snapshot,r.alpha);Path('/artifacts').mkdir(exist_ok=True);Path(f'/artifacts/run-{id}.json').write_text(json.dumps(result,ensure_ascii=False,allow_nan=False));r.result=result;r.error='';r.status=RunStatus.COMPLETED;db.commit()
    except Exception as exc:
        db.rollback();r=get_run(db,id);r.status=RunStatus.FAILED;r.error=str(exc)[:600];db.commit()
