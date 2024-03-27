from fastapi import Form
from pydantic import BaseModel


class UserResponse(BaseModel):
    userID: int = Form(...)
    studentID: str = Form(...)
    name: str = Form(...)
    password: str = Form(...)
    balance: int = Form(...)
    permissionID: int = Form(...)
    departmentID: int = Form(...)
    page: int = Form(...)
    sheet: int = Form(...)
    task: int = Form(...)


class AddBalanceRequest(BaseModel):
    userID: int = Form(...)
    cash: int = Form(...)
    balance: int = Form(...)
    # 0: add, 1: minus, 2: recoup
    type: int = Form(...)
    comment: str = Form(...)


class UserRequest(BaseModel):
    studentID: str = Form(...)
    name: str = Form(...)
    password: str = Form(...)
    departmentID: int = Form(...)
    permissionID: int = Form(...)
