#!/usr/bin/env python3
"""AXIOM DFIR: Autonomous Evidence-Verified Digital Forensics & Incident Response.

Target Event: Nebius x NVIDIA Global AI Hackathon 2026 (Best Apps & Agents Track).
Primary Command-Line Interface.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
# Add both root and subfolder src to path
sys.path.insert(0, str(HERE / "Axiom DFIR" / "src"))
sys.path.insert(0, str(HERE / "src"))
sys.path.insert(0, str(HERE / "Axiom DFIR"))

# Delegate to Axiom DFIR/axiom.py
import subprocess

if __name__ == "__main__":
    subscript = HERE / "Axiom DFIR" / "axiom.py"
    if subscript.is_file():
        result = subprocess.run([sys.executable, str(subscript)] + sys.argv[1:])
        sys.exit(result.returncode)
    else:
        print(f"Error: Could not locate {subscript}")
        sys.exit(1)

