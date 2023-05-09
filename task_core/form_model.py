from pydantic import BaseModel


class TaskAddForm(BaseModel):
    name: str
    command: str
    crontab_exp: str | None = None
    invoke_once: bool = False
