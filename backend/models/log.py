from fastapi import Form
from pydantic import BaseModel
from datetime import datetime

class PrintLogResponse(BaseModel):
    recordID: int = Form(...)
    userID: int = Form(...)
    time: datetime = Form(...)
    device: str = Form(...)
    size: int = Form(...)
    color: int = Form(...)
    duplex: int = Form(...)
    pages: int = Form(...)
    cost: int = Form(...)
    copies: int = Form(...)
    status: str = Form(...)

class DepositLogResponse(BaseModel):
    time: datetime = Form(...)
    userID: int = Form(...)
    cash: int = Form(...)
    balance: int = Form(...)
    _type: int = Form(...)
    comment: str = Form(...)