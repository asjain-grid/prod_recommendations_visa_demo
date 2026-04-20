from __future__ import annotations

import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[2]


def _load_env_file() -> None:
    env_path = BASE_DIR / ".env"
    if not env_path.exists():
        return

    for line in env_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


_load_env_file()

DATA_DIR = Path(os.getenv("DATA_DIR", str(BASE_DIR / "data"))).resolve()
PRODUCTS_DB_PATH = Path(
    os.getenv("PRODUCTS_DB_PATH", str(DATA_DIR / "products.db"))
).resolve()
CUSTOMER_DB_PATH = Path(
    os.getenv("CUSTOMER_DB_PATH", str(DATA_DIR / "customer_interactions.db"))
).resolve()

# API credential used by protected endpoints.
RECOMMENDATION_API_KEY = os.getenv("RECOMMENDATION_API_KEY", "")
