"""
Jarvis client — re-exports from shared.jarvis_client for backward compat.

Usage unchanged:
    from jarvis_client import Jarvis
    jarvis = Jarvis()
    result = await jarvis.ask("...")
"""

import sys
from pathlib import Path

# Ensure shared/ is importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from shared.jarvis_client import Jarvis, jarvis_ask  # noqa: F401
