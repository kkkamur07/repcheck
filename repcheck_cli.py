#!/usr/bin/env python3
import sys
from pathlib import Path

# Add the repcheck module to Python path
sys.path.insert(0, str(Path(__file__).parent))

from repcheck.main import app

if __name__ == "__main__":
    app()