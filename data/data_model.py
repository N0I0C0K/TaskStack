from sqlalchemy import Column, Float, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.decl_api import DeclarativeMeta

__all__ = ["SessionInfo", "TaskInfo", "as_dict"]


Base: DeclarativeMeta = declarative_base()
metadata = Base.metadata


def as_dict(obj: DeclarativeMeta) -> dict:
    t = obj.__dict__.copy()
    t.pop("_sa_instance_state")
    return t


class SessionInfo(Base):
    __tablename__ = "SessionInfo"

    id = Column(Text, primary_key=True)
    task_id = Column(Text, nullable=False, index=True)
    command = Column(Text, nullable=False)
    start_time = Column(Float, nullable=False)  # 触发时间 time.time()
    finish_time = Column(Float, nullable=False)
    success = Column(Boolean, nullable=True, default=False)

    def to_dict(self):
        return as_dict(self) | {"running": self.finish_time < self.start_time}

    @property
    def running(self):
        return self.finish_time < self.start_time

    @property
    def finish(self):
        return self.finish_time >= self.start_time


class TaskInfo(Base):
    __tablename__ = "TaskInfo"

    id = Column(Text, primary_key=True)
    name = Column(Text, nullable=False, index=True)
    active = Column(Boolean, nullable=False)
    create_time = Column(Float, nullable=False)
    command = Column(Text, nullable=False)
    crontab_exp = Column(Text, nullable=True)
