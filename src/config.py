import os
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_SCHEMA = os.getenv("DB_SCHEMA")
HEAD_URL = os.getenv("HEAD_URL")
ALLOWED_DOMAINS = os.getenv("ALLOWED_DOMAINS")
START_URLS = os.getenv("START_URLS")