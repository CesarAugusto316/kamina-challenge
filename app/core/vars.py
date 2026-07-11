from os import environ

from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = environ["DATABASE_URL"]
TEST_DATABASE_URL = environ["TEST_DATABASE_URL"]
JWT_SECRET = environ["JWT_SECRET"]
JWT_ALGORITHM = "HS256"
ALLOWED_ORIGIN = environ["ALLOWED_ORIGIN"] or "http://localhost:8080"
APP_ENV = environ["APP_ENV"] or "development"
