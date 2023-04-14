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
    invoke_time = Column(Float, nullable=False)  # 触发时间 time.time()
    finish_time = Column(Float, nullable=False)
    task_id = Column(Text, nullable=False)
    command = Column(Text, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "invoke_time": self.invoke_time,
            "finish_time": self.finish_time,
            "task_id": self.task_id,
            "command": self.command,
        }


class TaskInfo(Base):
    __tablename__ = "TaskInfo"

    id = Column(Text, primary_key=True)
    name = Column(Text, nullable=False)
    active = Column(Boolean, nullable=False)
    create_time = Column(Float, nullable=False)
    command = Column(Text, nullable=False)
    crontab_exp = Column(Text, nullable=True)
