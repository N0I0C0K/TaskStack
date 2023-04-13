from logging import ERROR

from sqlalchemy import create_engine
from sqlalchemy.log import rootlogger
from sqlalchemy.orm import Session

from .data_model import Base

from utils.file import db_path


class DataManager:
    def __init__(self) -> None:
        """
        数据管理, 采用sqllit进行数据储存
        """
        self.engine = create_engine(
            f"sqlite:///{db_path.as_posix()}", echo=False, future=True
        )
        rootlogger.setLevel(ERROR)
        self.create_all_table()

    def get_session(self) -> Session:
        return Session(self.engine)

    @property
    def session(self) -> Session:
        return self.get_session()

    def create_all_table(self):
        Base.metadata.create_all(self.engine)

    def remove_all_table(self):
        Base.metadata.drop_all(self.engine)


dataManager = DataManager()
"""
数据管理单例
负责数据的存储
"""
