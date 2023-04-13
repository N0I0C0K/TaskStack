from sqlalchemy import Column, Float, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base

__all__ = ["SessionInfo", "TaskInfo"]


Base = declarative_base()
metadata = Base.metadata


class SessionInfo(Base):
    __tablename__ = "SessionInfo"

    id = Column(Text, primary_key=True)
    invoke_time = Column(Float, nullable=False)  # 触发时间 time.time()
    finish_time = Column(Float, nullable=False)
    task_id = Column(Text, nullable=False)
    command = Column(Text, nullable=False)


class TaskInfo(Base):
    __tablename__ = "TaskInfo"

    id = Column(Text, primary_key=True)
    name = Column(Text, nullable=False)
    active = Column(Boolean, nullable=False)
    create_time = Column(Float, nullable=False)
    command = Column(Text, nullable=False)
    crontab_exp = Column(Text, nullable=True)
