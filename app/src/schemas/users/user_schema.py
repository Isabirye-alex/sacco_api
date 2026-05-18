from pydantic import BaseModel, ConfigDict, EmailStr
from datetime import date
from typing import Optional
from uuid import UUID


class UserCreate(BaseModel):
    # Auth Data (for user Model)
    role_id: UUID
    hashed_password: str
    

class UserSignIn(BaseModel):
    email: EmailStr
    password: str
    location_country: Optional[str] | None = None
    location_city: Optional[str] | None = None


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, validate_by_name=True)

    # Auth Data (for user Model)
    user_id: UUID
    email: EmailStr
    username: str
    first_name: str
    last_name: str
    # password: str

    # # Profile Date (for UserProfile)
    # member_id: str
    # phone_number: str
    # id_number: str
    # date_of_birth: date
    # occupation: str
    # monthly_income: str
    # marital_status: str
    # employer_name: str
    # primary_language: str

    # # Address Data (for UserAddress)
    # nationality: str
    # district : str
    # sub_county: str
    # parish: str
    # village: str
    # postal_code: str
