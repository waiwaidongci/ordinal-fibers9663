import hashlib,json,math
from src.services.rank_pool import pooled_rank_test
from src.services.dunn import dunn_all_pairs
from src.services.bootstrap_effects import winner_bootstrap,DEFAULT_SEED,DEFAULT_REPLICATES

def analyze_study(snapshot,alpha,bootstrap_seed=DEFAULT_SEED,bootstrap_replicates=DEFAULT_REPLICATES):
    if not math.isfinite(alpha) or not 0<alpha<1:raise ValueError('alpha须在0与1之间')
    treatments=sorted(snapshot['treatments'],key=lambda t:t['code']);readings=sorted(snapshot['readings'],key=lambda r:r['specimen_code'])
    if not 2<=len(treatments)<=5:raise ValueError('全部预定义工艺须为2–5组，不能事后挑组')
    if len(readings)>2000:raise ValueError('最多2000份独立试样')
    ids={t['id'] for t in treatments}
    if len(ids)!=len(treatments) or len({t['code'] for t in treatments})!=len(treatments):raise ValueError('工艺标识重复')
    if len({r['specimen_code'] for r in readings})!=len(readings):raise ValueError('试样标识重复，不能当作独立试样')
    for r in readings:
        x=r['grade']
        if r['treatment_id'] not in ids:raise ValueError('读数引用了研究之外的工艺')
        if isinstance(x,bool) or not isinstance(x,(float,int)) or not math.isfinite(x) or not 1<=x<=9 or int(x)!=x:raise ValueError('形成等级必须为1–9整数，非等距性能量')
    by_group=[[r for r in readings if r['treatment_id']==t['id']] for t in treatments]
    if any(len(g)<5 for g in by_group):raise ValueError('每个预定义工艺至少5份独立试样；不得丢掉空组')
    grades=[[r['grade'] for r in g] for g in by_group]
    pool=pooled_rank_test(grades);pairs=dunn_all_pairs(pool,alpha);groups=[];ranked=[]
    bootstrap=winner_bootstrap(grades,alpha,bootstrap_seed,bootstrap_replicates)
    for t,g,stats in zip(treatments,by_group,pool['groups']):
        ranks=stats.pop('ranks');frequency={str(k):sum(r['grade']==k for r in g) for k in range(1,10)};groups.append({**t,**stats,'grade_counts':frequency})
        ranked.extend({**r,'treatment_code':t['code'],'treatment_name':t['name'],'pooled_rank':rank} for r,rank in zip(g,ranks))
    for pair in pairs:pair.update(left_code=treatments[pair['i']]['code'],right_code=treatments[pair['j']]['code'],left_name=treatments[pair['i']]['name'],right_name=treatments[pair['j']]['name'])
    for bp,pair in zip(bootstrap['pairs'],pairs):
        pair.update(win_fraction=bp['win_fraction'],win_bootstrap_se=bp['bootstrap_se'],win_ci_lower=bp['ci_lower'],win_ci_upper=bp['ci_upper'],win_ci_covers_half=bp['ci_covers_half'],win_interval_method=bp['interval_method'],win_replicates_below_half=bp['replicates_below_half'],win_replicates_equal_half=bp['replicates_equal_half'],win_replicates_above_half=bp['replicates_above_half'])
    normalized_snapshot={'study':snapshot['study'],'treatments':treatments,'readings':readings}
    canonical={'algorithm':'pooled-kw-ties-dunn-holm-winner-bootstrap-v2','snapshot':normalized_snapshot,'alpha':alpha,'bootstrap_seed':bootstrap_seed,'bootstrap_replicates':bootstrap_replicates};fingerprint=hashlib.sha256(json.dumps(canonical,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
    return {**pool,'groups':groups,'pairs':pairs,'ranked_readings':ranked,'alpha':alpha,'omnibus_reject':pool['p_asymptotic']<=alpha,'family_size':len(pairs),'winner_effects':bootstrap,'fingerprint':fingerprint,'snapshot':normalized_snapshot,'p_method':'asymptotic chi-square KW and two-sided normal Dunn; not exact','scope':'independent ordinal samples; distributional differences may reflect shape, not only medians; win fraction is an ordinal direction effect, not a process-quality probability or causal conclusion'}
