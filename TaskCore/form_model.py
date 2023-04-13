from pydantic import BaseModel


class TaskAddForm(BaseModel):
    command: str
    input: str | None
