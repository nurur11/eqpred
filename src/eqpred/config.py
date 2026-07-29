from pathlib import Path

# Paths
PROJ_ROOT = Path(__file__).parents[2]

DATA_DIR = PROJ_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
RAW_BULLETIN_DIR = RAW_DATA_DIR / "bulletin"

INTERIM_DATA_DIR = DATA_DIR / "interim"
INTERIM_BULLETIN_PATH = INTERIM_DATA_DIR / "bulletin.pickle"
