"""
CareFlow — patient journey dashboard.

  python main.py              # Streamlit dashboard
  streamlit run streamlit_app.py
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def demo():
    app = ROOT / "streamlit_app.py"
    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT) + os.pathsep + env.get("PYTHONPATH", "")
    subprocess.run(
        [sys.executable, "-m", "streamlit", "run", str(app), "--server.headless", "true"],
        cwd=ROOT,
        env=env,
        check=False,
    )


if __name__ == "__main__":
    demo()
