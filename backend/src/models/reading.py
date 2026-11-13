from datetime import datetime
from sqlalchemy import String,ForeignKey,UniqueConstraint,DateTime,JSON
from sqlalchemy.dialects.mysql import DOUBLE
from sqlalchemy.orm import Mapped,mapped_column
from src.config.database import Base
class GradeReading(Base):
    __tablename__='grade_readings'
    id:Mapped[int]=mapped_column(primary_key=True)
    study_id:Mapped[int]=mapped_column(ForeignKey('grade_studies.id'))
    treatment_id:Mapped[int]=mapped_column(ForeignKey('treatments.id'))
    specimen_code:Mapped[str]=mapped_column(String(60))
    grade:Mapped[float]=mapped_column(DOUBLE(asdecimal=False))
    source_note:Mapped[str]=mapped_column(String(250),default='')
    __table_args__=(UniqueConstraint('study_id','specimen_code'),)
