from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

from careflow.data_loader import (
    data_available,
    load_encounters,
    load_patients,
    load_payers,
    load_providers,
    load_payer_transitions,
)
from careflow.models import JourneyState


@st.cache_data(show_spinner="Loading patient data…")
def cached_tables(data_dir: str) -> dict[str, pd.DataFrame]:
    root = Path(data_dir)
    return {
        "patients": load_patients(root),
        "encounters": load_encounters(root),
        "payer_transitions": load_payer_transitions(root),
        "payers": load_payers(root),
        "providers": load_providers(root),
    }


def init_session(data_dir: Path | None = None) -> dict[str, pd.DataFrame]:
    from careflow.data_loader import DEFAULT_DATA_DIR

    d = data_dir or DEFAULT_DATA_DIR
    if "careflow_tables" not in st.session_state:
        if data_available(d):
            st.session_state.careflow_tables = cached_tables(str(d))
        else:
            st.session_state.careflow_tables = {}
    if "careflow_journey" not in st.session_state:
        st.session_state.careflow_journey = JourneyState()
    return st.session_state.careflow_tables


def get_journey() -> JourneyState:
    return st.session_state.careflow_journey


def set_journey(state: JourneyState) -> None:
    st.session_state.careflow_journey = state


def reset_journey() -> None:
    st.session_state.careflow_journey = JourneyState()
