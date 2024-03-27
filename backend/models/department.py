from fastapi import Form
from pydantic import BaseModel


class DepartmentResponse(BaseModel):
    departmentID: int = Form(...)
    name: str = Form(...)
