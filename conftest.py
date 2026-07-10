"""Root conftest.py — ensure all packages are importable."""
import sys
from pathlib import Path

root = Path(__file__).parent
src_paths = [
    root / "packages" / "schema" / "src",
    root / "packages" / "engine" / "src",
    root / "packages" / "persistence" / "src",
    root / "packages" / "services" / "src",
    root / "packages" / "auth" / "src",
]

for p in src_paths:
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))
