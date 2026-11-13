from datetime import datetime
from sqlalchemy import String,ForeignKey,UniqueConstraint,DateTime,JSON
from sqlalchemy.dialects.mysql import DOUBLE
from sqlalchemy.orm import Mapped,mapped_column
from src.config.database import Base
class Treatment(Base):
    __tablename__='treatments'
    id:Mapped[int]=mapped_column(primary_key=True)
    study_id:Mapped[int]=mapped_column(ForeignKey('grade_studies.id'))
    code:Mapped[str]=mapped_column(String(40))
    name:Mapped[str]=mapped_column(String(100))
    process_note:Mapped[str]=mapped_column(String(1000),default='')
    __table_args__=(UniqueConstraint('study_id','code'),)
