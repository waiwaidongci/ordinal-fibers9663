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
    we=r.get('winner_effects')
    if we:
        w.writerow([])
        w.writerow(['winner_effect','bootstrap_seed','bootstrap_replicates','family_alpha','family_size','family_critical_radius','resampling','quantile_method','degenerate'])
        w.writerow([we['effect'],we['seed'],we['replicates'],we['family_alpha'],we['family_size'],we['family_critical_radius'],we['resampling'],we['quantile_method'],we['degenerate']])
        w.writerow(['left','right','left_win_fraction','ties_half_weighted','familywise_ci_lower','familywise_ci_upper','ci_covers_half_0.5','interval_method','direction_reading'])
        for pair in r['pairs']:
            if 'win_fraction' not in pair:continue
            direction=('\u5de6\u80dc\u65b9\u5411\uff0c\u533a\u95f4\u57280.5\u4e4b\u4e0a' if pair['win_ci_lower']>0.5 else '\u53f3\u80dc\u65b9\u5411\uff0c\u533a\u95f4\u57280.5\u4e4b\u4e0b' if pair['win_ci_upper']<0.5 else '\u533a\u95f4\u8de8\u8fc70.5\uff0c\u65b9\u5411\u672a\u5b9a')
            method_cn='\u6574\u65cf\u6700\u5927\u504f\u5dee\u767e\u5206\u4f4d' if pair['win_interval_method']=='bootstrap-family-max-deviation-percentile' else '\u9000\u5316\u70b9\u4f30\u8ba1\uff08\u65e0\u91cd\u62bd\u6837\u53d8\u5f02\uff09'
            w.writerow([pair['left_code'],pair['right_code'],pair['win_fraction'],'\u662f',pair['win_ci_lower'],pair['win_ci_upper'],pair['win_ci_covers_half'],method_cn,direction])
        w.writerow(['boundary','\u4f18\u80dc\u6bd4\u4f8b\u4e3a\u6709\u5e8f\u65b9\u5411\u6548\u5e94\uff08\u80dc+\u534a\u5e76\u5217\uff09/\u603b\u6bd4\u8f83\u6570\uff0c\u975e\u5de5\u827a\u8d28\u91cf\u6982\u7387\u6216\u56e0\u679c\u7ed3\u8bba\uff1b\u6574\u65cf\u6700\u5927\u504f\u5dee\u767e\u5206\u4f4d\u533a\u95f4\u4e3a\u8fd1\u4f3c\u540c\u65f6\u8986\u76d6\uff0c\u975e\u6709\u9650\u6837\u672c\u65e0\u6761\u4ef6\u4fdd\u8bc1\uff1b\u7b49\u7ea7\u79bb\u6563\u4f7f\u7f51\u683c\u7c97\u7cd9\u3001\u7aef\u70b9\u53ef\u80fd\u88ab\u622a\u65ad\u5230[0,1]\uff1b\u65e7\u7248\u7ed3\u679c\u4e0d\u542b\u672c\u8282\uff0c\u6309\u539f\u6837\u5206\u53d1\u4e0d\u8865\u7b97'])
    return '\ufeff'+out.getvalue()
