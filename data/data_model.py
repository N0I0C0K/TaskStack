from sqlalchemy import Column, Float, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship, Mapped
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.decl_api import DeclarativeMeta

__all__ = ["SessionInfo", "TaskInfo"]


Base: DeclarativeMeta = declarative_base()
metadata = Base.metadata


def as_dict(obj: DeclarativeMeta) -> dict:
    t = obj.__dict__.copy()
    t.pop("_sa_instance_state")
    return t


class SessionInfo(Base):
    __tablename__ = "SessionInfo"

    id = Column(Text, primary_key=True)
    task_id = Column(Text, ForeignKey("TaskInfo.id"))
    command = Column(Text, nullable=False)
    command_input = Column(Text, nullable=True)
    start_time = Column(Float, nullable=False)  # 触发时间 time.time()
    finish_time = Column(Float, nullable=False)
    success = Column(Boolean, nullable=True, default=False)
    task: Mapped["TaskInfo"] = relationship("TaskInfo", back_populates="sessions")

    def to_dict(self):
        return {
            "id": self.id,
            "task_id": self.task_id,
            "command": self.command,
            "command_input": self.command_input,
            "start_time": self.start_time,
            "finish_time": self.finish_time,
            "success": self.success,
            "running": self.finish_time < self.start_time,
        }

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
    command_input = Column(Text, nullable=True)
    comment = Column(Text, nullable=True)

    sessions: Mapped[list[SessionInfo]] = relationship(
        "SessionInfo", back_populates="task"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "active": self.active,
            "create_time": self.create_time,
            "command": self.command,
            "crontab_exp": self.crontab_exp,
            "command_input": self.command_input,
            "comment": self.comment,
        }
