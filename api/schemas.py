from pydantic import BaseModel, Field, EmailStr
from pydantic.types import StringConstraints
from typing import Annotated
from datetime import datetime


class ComplaintCreate(BaseModel):
    name: str = Field(..., min_length=1)
    phone_number: Annotated[str, StringConstraints(pattern=r"^\d{10}$")] = Field(...)
    email: EmailStr
    complaint_details: str = Field(..., min_length=1)


class ComplaintResponse(BaseModel):
    complaint_id: str
    name: str
    phone_number: str
    email: str
    complaint_details: str
    created_at: datetime

    class Config:
        orm_mode = True


class ComplaintIDResponse(BaseModel):
    complaint_id: str
    message: str
