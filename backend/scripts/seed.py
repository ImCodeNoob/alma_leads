"""Manual entrypoint to seed the attorney user, e.g. `python -m scripts.seed`.

The same seeding also runs automatically on API startup (see app/main.py);
this script exists for explicit invocation from the Docker entrypoint or CI.
"""

from app.database import Base, engine
from app.seed import seed_attorney_user

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    seed_attorney_user()
