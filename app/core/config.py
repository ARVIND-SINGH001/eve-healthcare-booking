import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    database_url = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg://postgres:postgres@localhost:5432/eve_healthcare",
    )
    jwt_secret = os.getenv("JWT_SECRET", "local-development-secret-change-me")
    jwt_algorithm = "HS256"
    access_token_minutes = 60


settings = Settings()
