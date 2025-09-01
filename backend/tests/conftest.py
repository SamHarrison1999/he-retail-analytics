import sys
from pathlib import Path

# Make the backend directory importable so "import src.…" works during test collection
BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))
