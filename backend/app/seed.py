import logging

from app.config import settings
from app.database import SessionLocal
from app.models import User
from app.security import hash_password

logger = logging.getLogger("seed")


def seed_attorney_user() -> None:
    """Idempotently ensure the seeded attorney account exists."""
    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.email == settings.attorney_email).first()
        if existing:
            return
        db.add(
            User(
                email=settings.attorney_email,
                hashed_password=hash_password(settings.attorney_password),
            )
        )
        db.commit()
        logger.info("Seeded attorney user %s", settings.attorney_email)
    finally:
        db.close()
