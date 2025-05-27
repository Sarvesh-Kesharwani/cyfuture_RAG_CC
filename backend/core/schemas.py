from pydantic import BaseModel, EmailStr, constr, Field, model_validator
from typing import Annotated
from datetime import datetime


# Request schema for complaint creation
class ComplaintCreate(BaseModel):
    name: constr(min_length=1)
    phone_number: str
    email: EmailStr
    complaint_details: constr(min_length=1)

    @model_validator(mode="before")
    def check_phone_number(cls, values):
        phone = values.get("phone_number")
        if phone and (len(phone) != 10 or not phone.isdigit()):
            raise ValueError("Phone number must be 10 digits.")
        return values


# Response schema for single complaint retrieval
class ComplaintResponse(BaseModel):
    complaint_id: str
    name: str
    phone_number: str
    email: str
    complaint_details: str
    created_at: datetime  # <-- use datetime, not str

    class Config:
        orm_mode = True


# Response schema after creating a complaint
class ComplaintIDResponse(BaseModel):
    complaint_id: str
    message: str
