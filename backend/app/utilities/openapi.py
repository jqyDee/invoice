import json
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BASE_DIR))

from app.main import app  # noqa: E402
from app.utilities import OPENAPI_JSON_FRONTEND_PATH  # noqa: E402

output_file = OPENAPI_JSON_FRONTEND_PATH

# Ensure directory exists
output_file.parent.mkdir(parents=True, exist_ok=True)

with open(output_file, "w", encoding="utf-8") as f:
    json.dump(app.openapi(), f, indent=2, ensure_ascii=False)

print(f"OpenAPI JSON written to {output_file}")
