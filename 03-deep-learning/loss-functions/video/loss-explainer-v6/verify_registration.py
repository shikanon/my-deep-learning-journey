"""Compatibility entry point for fixed-smile rig verification."""
import runpy
from pathlib import Path
runpy.run_path(str(Path(__file__).with_name("verify_rig.py")),run_name="__main__")
