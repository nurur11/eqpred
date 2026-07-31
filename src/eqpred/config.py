from pathlib import Path

# Paths
PROJ_ROOT = Path(__file__).parents[2]

DATA_DIR = PROJ_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
RAW_BULLETIN_DIR = RAW_DATA_DIR / "bulletin"
RAW_DAILY_MAP_DIR = RAW_DATA_DIR / "daily_map"

INTERIM_DATA_DIR = DATA_DIR / "interim"
INTERIM_BULLETIN_PATH = INTERIM_DATA_DIR / "bulletin.pickle"
INTERIM_DAILY_MAP_PATH = INTERIM_DATA_DIR / "daily_map.pickle"
