"""Compatibility entry point: build the fixed-smile reusable V3 rig."""
import runpy
from pathlib import Path
runpy.run_path(str(Path(__file__).with_name("rig_author.py")),run_name="__main__")
