from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str

    # Email Configuration
    SMTP_SERVER: str = "smtp.gmail.com"
    SMTP_PORT: int = 465
    SENDER_EMAIL: Optional[str] = None
    SENDER_PASSWORD: Optional[str] = None

    # SMS Gateway Configuration - Africa's Talking
    AFRICAS_TALKING_API_KEY: Optional[str] = None
    AFRICAS_TALKING_SENDER_ID: Optional[str] = "SACCO"

    # SMS Gateway Configuration - Twilio
    TWILIO_ACCOUNT_SID: Optional[str] = None
    TWILIO_AUTH_TOKEN: Optional[str] = None
    TWILIO_PHONE_FROM: Optional[str] = None

    # Mobile Money Configuration
    MOBILE_MONEY_API_KEY: Optional[str] = None
    MOBILE_MONEY_API_SECRET: Optional[str] = None
    MOBILE_MONEY_PROVIDER: str = "mpesa"  # mpesa, airtel_money, etc.

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
