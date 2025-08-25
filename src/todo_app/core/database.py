import os

from dotenv import load_dotenv

load_dotenv()

# os.getenv= 環境変数を見てね
DB_CONNECTION = os.getenv("DB_CONNECTION", "")
DB_USERNAME = os.getenv("DB_USERNAME", "")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_HOST = os.getenv("DB_HOST", "")
DB_PORT = os.getenv("DB_PORT", "")
DB_DATABASE = os.getenv("DB_DATABASE", "")

DATABASE_URL = (
    DB_CONNECTION
    + "://"
    + DB_USERNAME
    + ":"
    + DB_PASSWORD
    + "@"
    + DB_HOST
    + ":"
    + DB_PORT
    + "/"
    + DB_DATABASE
)
