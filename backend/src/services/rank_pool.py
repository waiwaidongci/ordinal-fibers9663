"""All groups share one pooled average-rank system; integer tie terms."""
import numpy as np
from scipy.stats import rankdata,chi2

def pooled_rank_test(groups):
    if not 2<=len(groups)<=5 or any(len(g)==0 for g in groups):raise ValueError('须有2–5个非空组')
    arrays=[np.asarray(g,dtype=float) for g in groups]
    if any(g.ndim!=1 or not np.isfinite(g).all() for g in arrays):raise ValueError('等级必须是一维有限值')
    values=np.concatenate(arrays);n=len(values);ranks=rankdata(values,method='average');unique,counts=np.unique(values,return_counts=True)
    tie_term=sum(int(t)**3-int(t) for t in counts);denom=n**3-n;tie_numerator=denom-tie_term
    if tie_numerator==0:raise ValueError('全部等级相同，C=0；Kruskal–Wallis与Dunn统计量未定义')
    correction=tie_numerator/denom;variance=tie_numerator/(12*(n-1));rows=[];offset=0
    for g in arrays:
        rg=ranks[offset:offset+len(g)];ordered=np.sort(g);offset+=len(g)
        rows.append({'n':len(g),'rank_sum':float(rg.sum()),'mean_rank':float(rg.mean()),'median_lower':float(ordered[(len(g)-1)//2]),'median_upper':float(ordered[len(g)//2]),'ranks':rg.tolist()})
    # Centered expression avoids subtracting almost equal large rank sums.
    raw=12/(n*(n+1))*sum(r['n']*(r['mean_rank']-(n+1)/2)**2 for r in rows);h=raw/correction;p=float(chi2.sf(h,len(groups)-1))
    ties=[{'grade':float(v),'count':int(t),'average_rank':float(ranks[values==v][0]),'term':int(t)**3-int(t)} for v,t in zip(unique,counts)]
    return {'n':n,'k':len(groups),'h_raw':raw,'h':h,'df':len(groups)-1,'p_asymptotic':p,'p_underflow':p==0,'tie_term':tie_term,'tie_correction':correction,'dunn_variance':variance,'ties':ties,'groups':rows}
