import os
from pathlib import Path

# --- General Configuration ---
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
CACHE_DIR = PROJECT_ROOT / "cache"
LOGS_DIR = PROJECT_ROOT / "logs"

# Ensure directories exist
for d in [DATA_DIR, CACHE_DIR, LOGS_DIR]:
    d.mkdir(exist_ok=True)

# --- Algorithm Parameters ---
ALPHA = 0.7  # Weight for content-based score (1 - ALPHA is for collaborative)
TOP_K_CF = 10  # Number of nearest neighbors to store for item-item CF
POSITIVE_RATING_THRESHOLD = 4.0  # Minimum rating to consider an item "liked" by a user

# --- Content Vectorizer Parameters ---
TFIDF_MAX_FEATURES = 5000
# Stopwords: Using English as a default, as the data might be mixed or predominantly English-based
# for common recommendation datasets. The user specified to configure for ukrainian/english.
# Since we don't have a definitive list for Ukrainian, we'll use a common English list
# and rely on TF-IDF's ability to handle common words.
TFIDF_STOP_WORDS = 'english' 

# --- File Paths ---
ITEMS_FILE = DATA_DIR / "items.csv"
USERS_FILE = DATA_DIR / "users.csv"
RATINGS_FILE = DATA_DIR / "ratings.csv"

# --- Cache Paths ---
ITEM_VECTORS_CACHE = CACHE_DIR / "item_vectors.pkl"
ITEM_CF_SIM_CACHE = CACHE_DIR / "item_cf_sim.pkl"
METADATA_CACHE = CACHE_DIR / "metadata.pkl"

# --- Logging Configuration ---
LOG_FILE = LOGS_DIR / "app.log"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
DEFAULT_LOG_LEVEL = "INFO"
DEBUG_LOG_LEVEL = "DEBUG"
