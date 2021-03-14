import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

sys.path.insert(0, BASE_DIR)
sys.path.insert(1, BASE_DIR / ".venv/lib/python3.9/site-packages")

from eclair import wsgi

application = wsgi.application
