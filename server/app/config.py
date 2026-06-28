import os
from dotenv import load_dotenv

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
ASTRA_DB_APPLICATION_TOKEN = os.getenv("ASTRA_DB_APPLICATION_TOKEN", os.getenv("astra_db_application_token"))
ASTRA_DB_API_ENDPOINT = os.getenv("ASTRA_DB_API_ENDPOINT", os.getenv("astra_db_api_endpoint"))
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")

if not ASTRA_DB_APPLICATION_TOKEN:
    raise ValueError("ASTRA_DB_APPLICATION_TOKEN environment variable is required")
if not ASTRA_DB_API_ENDPOINT:
    raise ValueError("ASTRA_DB_API_ENDPOINT environment variable is required")
