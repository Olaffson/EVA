import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

EVA_API_URL = os.getenv("EVA_API_URL", "https://api.eva.gg/graphql")
EVA_APP_ORIGIN = os.getenv("EVA_APP_ORIGIN", "https://app.eva.gg")
EVA_EMAIL = os.getenv("EVA_EMAIL")
EVA_PASSWORD = os.getenv("EVA_PASSWORD")
TOKEN_STORE_PATH = Path(os.getenv("EVA_TOKEN_STORE", ".eva_tokens.json"))
DB_PATH = Path(os.getenv("EVA_DB_PATH", "eva.db"))
