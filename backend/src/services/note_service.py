import csv,io
from sqlalchemy import select
from fastapi import HTTPException
from src.models import FollowupNote
from src.services.run_service import get_run
from src.constants.enums import NoteStatus

def list_notes(db):return db.scalars(select(FollowupNote).order_by(FollowupNote.id.desc())).all()
def create_note(db,data):
    r=get_run(db,data.run_id)
    if r.status!='completed':raise HTTPException(409,'仅完成任务可作为复检说明依据')
    if db.scalar(select(FollowupNote).where(FollowupNote.name==data.name)):raise HTTPException(409,'复检说明名称重复')
    n=FollowupNote(**data.model_dump());db.add(n);db.commit();return n

def review_note(db,id,data,user):
    n=db.get(FollowupNote,id)
    if not n:raise HTTPException(404,'复检说明不存在')
    if n.status!=NoteStatus.DRAFT:raise HTTPException(409,'已审阅决定不可覆盖，请新建修订')
    if data.status not in (NoteStatus.APPROVED,NoteStatus.REJECTED):raise HTTPException(422,'请选择同意或退回')
    n.status=data.status;n.reviewer_note=data.reviewer_note;n.reviewed_by=user.email;db.commit();return n

def export_note(db,id):
    n=db.get(FollowupNote,id)
    if not n:raise HTTPException(404,'复检说明不存在')
    if n.status!=NoteStatus.APPROVED:raise HTTPException(409,'批准后才可分发CSV')
    run=get_run(db,n.run_id);r=run.result;out=io.StringIO();w=csv.writer(out)
    w.writerow(['note','reviewer','reviewer_note','rationale','fingerprint','scope']);w.writerow([n.name,n.reviewed_by,n.reviewer_note,n.rationale,r['fingerprint'],'等级非等距；独立样本；全部组对；渐近p非exact；不作工艺因果或性能概率'])
    w.writerow(['N','k','H_raw','tie_C','H_corrected','df','p_asymptotic','alpha','family_size','tie_term','dunn_variance']);w.writerow([r['n'],r['k'],r['h_raw'],r['tie_correction'],r['h'],r['df'],r['p_asymptotic'],r['alpha'],r['family_size'],r['tie_term'],r['dunn_variance']])
    w.writerow(['group','name','n','rank_sum','mean_rank','median_lower_grade','median_upper_grade'])
    for g in r['groups']:w.writerow([g[k] for k in ['code','name','n','rank_sum','mean_rank','median_lower','median_upper']])
    w.writerow(['left','right','mean_rank_difference','standard_error','z','p_raw_asymptotic','p_holm','reject'])
    for pair in r['pairs']:w.writerow([pair[k] for k in ['left_code','right_code','mean_rank_difference','standard_error','z','p_raw_asymptotic','p_holm','reject']])
    return '\ufeff'+out.getvalue()
