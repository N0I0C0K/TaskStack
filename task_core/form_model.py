from pydantic import BaseModel


class TaskAddForm(BaseModel):
    name: str
    command: str
