"""Dunn contrasts use pooled mean ranks and a fixed whole-family Holm map."""
import math
from itertools import combinations
from scipy.stats import norm

def holm_adjust(p_values):
    m=len(p_values)
    if not m or any(not math.isfinite(p) or p<0 or p>1 for p in p_values):raise ValueError('Holm输入须为有限p值')
    order=sorted(range(m),key=lambda i:p_values[i]);result=[0.]*m;running=0.
    for j,i in enumerate(order):running=max(running,min(1.,(m-j)*p_values[i]));result[i]=running
    return result

def dunn_all_pairs(pool,alpha):
    rows=[]
    for i,j in combinations(range(pool['k']),2):
        a,b=pool['groups'][i],pool['groups'][j];se=math.sqrt(pool['dunn_variance']*(1/a['n']+1/b['n']));delta=a['mean_rank']-b['mean_rank'];z=delta/se;p=float(2*norm.sf(abs(z)))
        rows.append({'i':i,'j':j,'mean_rank_difference':delta,'standard_error':se,'z':z,'p_raw_asymptotic':p,'p_underflow':p==0})
    adjusted=holm_adjust([r['p_raw_asymptotic'] for r in rows])
    for row,p in zip(rows,adjusted):row.update(p_holm=p,reject=bool(p<=alpha))
    return rows
