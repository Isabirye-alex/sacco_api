from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str
    ONLINE_DATABASE_URL: str

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

    # Mobile Money Configuration (MarzPay only)
    MARZPAY_API_URL: Optional[str] = "https://wallet.wearemarz.com/api/v1/collect-money"
    MARZPAY_CALLBACK_URL: Optional[str] = None
    MARZPAY_COUNTRY: str = "UG"
    API_BASE_URL: Optional[str] = None
    MOBILE_MONEY_PROVIDER: str = "marzpay"
    MARZPAY_AUTH_HEADER: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
