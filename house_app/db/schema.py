from pydantic import BaseModel, EmailStr
from typing import Optional
from enum import Enum
from datetime import datetime

class StatusChoices(str, Enum):
    client = 'client'
    owner = 'owner'

class UserCreateSchema(BaseModel):
    first_name: str
    last_name: str
    username: str
    password: str  # не hash_password, а обычный ввод пароля
    phone_number: Optional[str] = None
    age: Optional[int] = None
    profile_image: Optional[str] = None
    status: StatusChoices = StatusChoices.client

    class Config:
        from_attributes = True

class UserResponseSchema(BaseModel):
    id: int
    first_name: str
    last_name: str
    username: str
    phone_number: Optional[str] = None
    age: Optional[int] = None
    profile_image: Optional[str] = None
    status: StatusChoices
    date_registered: datetime

    class Config:
        from_attributes = True


class HouseDataSchema(BaseModel):
    GrLivArea: int
    YearBuilt: int
    GarageCars: int
    TotalBsmtSF: int
    FullBath: int
    OverallQual: int

    class Config:
        from_attributes = True
