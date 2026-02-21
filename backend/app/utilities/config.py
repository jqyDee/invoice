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

# These are obviously fake
BANK_SETTINGS = {
    "iban": "DE12 3456 7890 1234 56",
    "bic": "AABBCC",
    "steuer_id": "123/456/789"
}