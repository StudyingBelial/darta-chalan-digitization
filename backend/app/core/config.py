import os
try:
    from pydantic_settings import BaseSettings, SettingsConfigDict
except ImportError:
    from pydantic import BaseModel as BaseSettings
    SettingsConfigDict = None

class Settings(BaseSettings):
    PROJECT_NAME: str = "Darta-Chalan Digitization System"
    VERSION: str = "1.0.0"
    
    # Server Binding
    HOST: str = os.getenv("HOST", os.getenv("APP_HOST", "0.0.0.0"))
    PORT: int = int(os.getenv("PORT", os.getenv("APP_PORT", "8000")))
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./digitization.db")
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "MY_SUPER_DUPER_SECRET_KEY_REPLACE_IN_PROD")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "15"))
    REFRESH_TOKEN_EXPIRE_HOURS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_HOURS", "12"))
    
    # File Storage
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "./storage/uploads")
    MAX_UPLOAD_SIZE_MB: int = int(os.getenv("MAX_UPLOAD_SIZE_MB", "25"))
    
    # OCR Engine
    TESSERACT_CMD: str = os.getenv("TESSERACT_CMD", "")

    # Inbound SMTP Scanner (Scan-to-Email receiver for Canon/MFP hardware scanners)
    SMTP_SCANNER_ENABLED: bool = os.getenv("SMTP_SCANNER_ENABLED", "true").lower() in ("true", "1", "yes")
    SMTP_SCANNER_HOST: str = os.getenv("SMTP_SCANNER_HOST", "0.0.0.0")
    SMTP_SCANNER_PORT: int = int(os.getenv("SMTP_SCANNER_PORT", "1025"))
    SMTP_SCANNER_MAX_MESSAGE_MB: int = int(os.getenv("SMTP_SCANNER_MAX_MESSAGE_MB", "25"))
    SMTP_SCANNER_ALLOWED_DOMAINS: str = os.getenv("SMTP_SCANNER_ALLOWED_DOMAINS", "")
    SMTP_SCANNER_DEFAULT_OFFICE_ID: int = int(os.getenv("SMTP_SCANNER_DEFAULT_OFFICE_ID", "1"))

    # Outbound SMTP / Email Notifications
    OUTBOUND_EMAIL_ENABLED: bool = os.getenv("OUTBOUND_EMAIL_ENABLED", "false").lower() in ("true", "1", "yes")
    OUTBOUND_SMTP_HOST: str = os.getenv("OUTBOUND_SMTP_HOST", "")
    OUTBOUND_SMTP_PORT: int = int(os.getenv("OUTBOUND_SMTP_PORT", "587"))
    OUTBOUND_SMTP_USER: str = os.getenv("OUTBOUND_SMTP_USER", "")
    OUTBOUND_SMTP_PASSWORD: str = os.getenv("OUTBOUND_SMTP_PASSWORD", "")
    OUTBOUND_SMTP_FROM: str = os.getenv("OUTBOUND_SMTP_FROM", "darta@ntc.net.np")
    OUTBOUND_SMTP_USE_TLS: bool = os.getenv("OUTBOUND_SMTP_USE_TLS", "true").lower() in ("true", "1", "yes")

    # CORS
    CORS_ORIGINS: list[str] = ["*"]

    if SettingsConfigDict:
        model_config = SettingsConfigDict(
            env_file=".env",
            env_file_encoding="utf-8",
            extra="ignore"
        )

settings = Settings()
