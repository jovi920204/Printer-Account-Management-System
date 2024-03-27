from fastapi import Form
from pydantic import BaseModel

class PrintRequest(BaseModel):
    studentID: str = Form(...)
    printer: int = Form(...)
    size: int = Form(...)
    color: int = Form(...)
    duplex: int = Form(...)
    pages: int = Form(...)
    copies: int = Form(...)

class CallbackStatus(BaseModel):
    user_id: int = Form(...)
    time: str = Form(...)
    status: str = Form(...)