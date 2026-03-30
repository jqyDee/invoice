import os
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[3]
BASE_DIR = Path(__file__).resolve().parents[2]

# DIRS
CACHE_DIR = BASE_DIR / "cache" / "pdfs"
TEMP_DIR = BASE_DIR / "temp"
FRONTEND_DIR = ROOT_DIR / "frontend"
DATA_DIR = BASE_DIR / "data"

ASSETS_DIR = BASE_DIR / "assets"
FONTS_DIR = ASSETS_DIR / "fonts"
IMAGES_DIR = ASSETS_DIR / "images"

# DIR CREATION
ASSETS_DIR.mkdir(parents=True, exist_ok=True)
IMAGES_DIR.mkdir(parents=True, exist_ok=True)
CACHE_DIR.mkdir(parents=True, exist_ok=True)
TEMP_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)

# ASSET PATHS
LOGO_PATH = IMAGES_DIR / "logo.png"
DB_PATH = DATA_DIR / "db.db"
OPENAPI_JSON_FRONTEND_PATH = FRONTEND_DIR / "openapi.json"

# PDF CONFIG
NORMAL_FONT_SIZE = 11
TREATMENT_FONT_SIZE = 10
RECIPIENT_OFFSET = 4
INVOICE_FOOTER_FONT_SIZE = 8  # 8 - 11, 8 is prev default

DOCUMENT_FONT_SIZE = 8
DOCUMENT_HEADER_FONT_SIZE = 10
DOCUMENT_DEFAULT_OFFSET = 6
DOCUMENT_IN_TEXT_OFFSET = 3

# ACCESS
JWT_SECRET = os.getenv("JWT_SECRET", "change-me-in-production")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRY", 20))
JWT_ALGORITHM = "HS256"

# SENTRY
SENTRY_DSN = os.getenv("PYTHON_SENTRY_DSN")
