import os
import yaml
from groq import Groq

# Get the exact path for yml - C:\PythonProject\RealEstate\rag
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Point directly to the YAML file in that same folder -C:\PythonProject\RealEstate\rag\rag_config.yml
YML_FILE = os.path.join(BASE_DIR, "rag_config.yml")

# Check if it exists
if not os.path.exists(YML_FILE):
    raise FileNotFoundError(f"Config file '{YML_FILE}' not found! "
                            f"Make sure it is in {BASE_DIR}")

with open(YML_FILE) as f:
    cfg = yaml.safe_load(f)

# Global dictionaries for easy import across scripts
DB_CONFIG = cfg.get("postgres", {})
API_CONFIG = cfg.get("api", {})

# Initialize Groq client
GROQ_API_KEY = API_CONFIG.get("groq_key")
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY is missing from rag_config.yml!")

client = Groq(api_key=GROQ_API_KEY)
