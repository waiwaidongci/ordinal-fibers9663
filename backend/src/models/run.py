from datetime import datetime
from sqlalchemy import String,ForeignKey,UniqueConstraint,DateTime,JSON
from sqlalchemy.dialects.mysql import DOUBLE
from sqlalchemy.orm import Mapped,mapped_column
from src.config.database import Base
class RankTestRun(Base):
    __tablename__='rank_test_runs'
    id:Mapped[int]=mapped_column(primary_key=True)
    name:Mapped[str]=mapped_column(String(140),unique=True)
    study_id:Mapped[int]=mapped_column(ForeignKey('grade_studies.id'))
    alpha:Mapped[float]=mapped_column(DOUBLE(asdecimal=False),default=.05)
    bootstrap_seed:Mapped[int]=mapped_column(default=20261113)
    bootstrap_replicates:Mapped[int]=mapped_column(default=9999)
    status:Mapped[str]=mapped_column(String(20),default='queued')
    snapshot:Mapped[dict]=mapped_column(JSON,default=dict)
    result:Mapped[dict]=mapped_column(JSON,default=dict)
    error:Mapped[str]=mapped_column(String(600),default='')
    created_at:Mapped[datetime]=mapped_column(DateTime,default=datetime.utcnow)
