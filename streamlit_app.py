"""CareFlow Streamlit dashboard — run: streamlit run streamlit_app.py"""

from pathlib import Path

from careflow.dashboard import run_dashboard

if __name__ == "__main__":
    run_dashboard(Path(__file__).resolve().parent / "output" / "csv")
