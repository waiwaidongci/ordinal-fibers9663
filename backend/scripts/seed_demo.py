"""Insert-only natural keys; 360 independent synthetic specimens, no saved tests."""
import numpy as np
from sqlalchemy import select
from src.config.database import Base,engine,Session
from src.models import User,GradeStudy,Treatment,GradeReading
from src.utils.security import hash_password

def seed():
    Base.metadata.create_all(engine)
    with Session() as db:
        for role,name in [('admin','宋槐 · 复检负责人'),('analyst','林蘖 · 检验分析员'),('viewer','周予 · 纸材观察员')]:
            email=role+'@qingnie.local'
            if not db.scalar(select(User).where(User.email==email)):db.add(User(email=email,name=name,role=role,password_hash=hash_password('Qingnie2026!')))
        rng=np.random.default_rng(20261112)
        probabilities=[[.05,.15,.25,.25,.2,.07,.03,0,0],[0,.03,.07,.15,.25,.25,.15,.08,.02],[0,.02,.05,.12,.21,.26,.18,.11,.05],[0,0,.01,.03,.06,.12,.25,.28,.25]]
        for scode,title in [('QN-SHIFT','形成错位 · 四工艺复检研究'),('QN-NEAR','相近分布 · 平行批研究'),('QN-CONST','全同等级 · 未定义边界')]:
            s=db.scalar(select(GradeStudy).where(GradeStudy.code==scode))
            if not s:s=GradeStudy(code=scode,name=title,source_file=scode+'_独立纸浆试样.csv',protocol='形成等级1至9仅有顺序，1为粗散、9为均整；每份试样只评一次，全部预定义工艺进入同一检验。');db.add(s);db.flush()
            for g,name in enumerate(['清水参照','温和酶解','低剪切打浆','复合处理']):
                code='T'+str(g+1);t=db.scalar(select(Treatment).where(Treatment.study_id==s.id,Treatment.code==code))
                if not t:t=Treatment(study_id=s.id,code=code,name=name,process_note='独立制备、盲评形成等级；不能把等级差当作等距性能变化。');db.add(t);db.flush()
                probs=probabilities[g] if scode=='QN-SHIFT' else [.02,.04,.08,.16,.25,.22,.14,.07,.02]
                values=rng.choice(np.arange(1,10),size=30,p=probs) if scode!='QN-CONST' else np.full(30,5)
                for i,x in enumerate(values):
                    specimen=f'{scode}-{code}-{i+1:03}'
                    if not db.scalar(select(GradeReading).where(GradeReading.study_id==s.id,GradeReading.specimen_code==specimen)):db.add(GradeReading(study_id=s.id,treatment_id=t.id,specimen_code=specimen,grade=float(x),source_note=s.source_file))
        db.commit()
if __name__=='__main__':seed();print('seed insert-only complete')
