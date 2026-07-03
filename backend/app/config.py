from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Storage
    database_url: str = "sqlite:///./app.db"
    upload_dir: str = "./uploads"
    max_resume_size_bytes: int = 5 * 1024 * 1024

    # Auth
    jwt_secret: str = "dev-secret-change-me-please-use-a-long-random-value"
    jwt_algorithm: str = "HS256"
    jwt_expires_minutes: int = 60 * 12

    # Seeded attorney account (created on startup if it doesn't exist)
    attorney_email: str = "attorney@example.com"
    attorney_password: str = "changeme123"

    # Shared invite code required to register a new attorney account.
    # Registering grants access to every lead's PII and resume, so this
    # isn't left open to anyone who finds /register.
    attorney_signup_code: str = "change-me-invite-code"

    # Email
    smtp_host: str | None = None
    smtp_port: int = 587
    smtp_username: str | None = None
    smtp_password: str | None = None
    smtp_from: str = "no-reply@example.com"
    smtp_use_tls: bool = True
    fallback_email_dir: str = "./emails"

    # CORS
    cors_origins: str = "http://localhost:3000"

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


settings = Settings()
