from fastapi import Form
from pydantic import BaseModel


class PermisstionResponse(BaseModel):
    permissionID: int = Form(...)
    name: str = Form(...)
    management: bool = Form(...)
    _print: bool = Form(...)
