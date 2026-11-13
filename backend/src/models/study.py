from datetime import datetime
from sqlalchemy import String,ForeignKey,UniqueConstraint,DateTime,JSON
from sqlalchemy.dialects.mysql import DOUBLE
from sqlalchemy.orm import Mapped,mapped_column
from src.config.database import Base
class GradeStudy(Base):
    __tablename__='grade_studies'
    id:Mapped[int]=mapped_column(primary_key=True)
    code:Mapped[str]=mapped_column(String(40),unique=True)
    name:Mapped[str]=mapped_column(String(140))
    protocol:Mapped[str]=mapped_column(String(1200),default='')
    source_file:Mapped[str]=mapped_column(String(140),default='')
