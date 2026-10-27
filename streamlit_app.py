# Run the page afresh on every Streamlit rerun; normal imports are cached.
from pathlib import Path
import runpy

runpy.run_path(str(Path(__file__).with_name("app.py")), run_name="__main__")
