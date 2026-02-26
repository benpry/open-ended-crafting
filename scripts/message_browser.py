"""
Message Browser — Streamlit app for reading human chain messages.

Run with:
    streamlit run scripts/message_browser.py
"""

import pandas as pd
import streamlit as st
from pyprojroot import here

st.set_page_config(page_title="Message Browser", layout="wide")

TAG_LABELS = {
    "abstractions_lm": "abstract",
    "concrete_recipes_lm": "recipe",
    "positive_valence_lm": "+valence",
    "negative_valence_lm": "-valence",
    "policy_lm": "policy",
    "dynamics_lm": "dynamics",
    "avoidance_lm": "avoidance",
}


@st.cache_data
def load_data() -> pd.DataFrame:
    msgs = pd.read_csv(
        here("data/human-data/experiment-1/processed/messages.csv")
    )
    tags = pd.read_csv(
        here("data/human-data/experiment-1/processed_old/messages_lm_tags.csv")
    )
    gameplay = pd.read_csv(
        here("data/human-data/experiment-1/processed/gameplay.csv")
    )

    tag_cols = ["trial_id"] + list(TAG_LABELS.keys())
    df = msgs.merge(tags[tag_cols], on="trial_id", how="left")

    scores = (
        gameplay.groupby("trial_id")["score"]
        .agg(
            mean_score="mean",
            max_score="max",
            pct_100=lambda s: 100 * (s == 100).mean(),
        )
        .reset_index()
    )
    return df.merge(scores, on="trial_id", how="left")


def render_message_card(row) -> None:
    with st.container(border=True):
        mean_s = row.get("mean_score")
        max_s = row.get("max_score")
        pct = row.get("pct_100")
        if pd.notna(mean_s):
            st.caption(f"avg {mean_s:.0f} · peak {max_s:.0f} · {pct:.0f}% perfect")
        msg = row.get("message", "")
        st.write(msg if isinstance(msg, str) else "_No message_")
        active_tags = [
            label
            for col, label in TAG_LABELS.items()
            if col in row and row[col] is True
        ]
        if active_tags:
            st.caption("Tags: " + " · ".join(active_tags))


df = load_data()

# ── Sidebar ──────────────────────────────────────────────────────────────────
st.sidebar.title("Message Browser")

domain_choice = st.sidebar.radio(
    "Domain",
    ["All", "potions", "cooking", "decorations", "animals"],
)
condition_choice = st.sidebar.radio("Condition", ["chain", "individual"])

filtered = df[df["condition"] == condition_choice].copy()
if domain_choice != "All":
    filtered = filtered[filtered["domain"] == domain_choice]

# Reset navigation index when filters change
filter_key = (domain_choice, condition_choice)
if st.session_state.get("_last_filter") != filter_key:
    st.session_state["chain_idx"] = 0
    st.session_state["_last_filter"] = filter_key

if "chain_idx" not in st.session_state:
    st.session_state["chain_idx"] = 0

# ── Chain condition ──────────────────────────────────────────────────────────
if condition_choice == "chain":
    chain_ids = sorted(filtered["chain_id"].unique())
    if not chain_ids:
        st.warning("No chains found for this selection.")
        st.stop()

    idx = st.session_state["chain_idx"]
    idx = max(0, min(idx, len(chain_ids) - 1))

    col_prev, col_info, col_next = st.columns([1, 6, 1])
    with col_prev:
        if st.button("← Prev", disabled=(idx == 0)):
            st.session_state["chain_idx"] = idx - 1
            st.rerun()
    with col_next:
        if st.button("Next →", disabled=(idx == len(chain_ids) - 1)):
            st.session_state["chain_idx"] = idx + 1
            st.rerun()
    with col_info:
        st.markdown(
            f"<div style='text-align:center; padding-top:6px'>"
            f"Chain <b>{idx + 1}</b> of <b>{len(chain_ids)}</b>"
            f"</div>",
            unsafe_allow_html=True,
        )

    chain_id = chain_ids[idx]
    chain_df = (
        filtered[filtered["chain_id"] == chain_id]
        .sort_values("chain_pos")
        .reset_index(drop=True)
    )
    domain = chain_df["domain"].iloc[0]

    st.title(f"Chain {chain_id} — {domain}")

    for _, row in chain_df.iterrows():
        st.markdown(f"**Position {int(row['chain_pos'])}**")
        render_message_card(row)

# ── Individual condition ─────────────────────────────────────────────────────
else:
    rows = filtered.reset_index(drop=True)
    if rows.empty:
        st.warning("No messages found for this selection.")
        st.stop()

    idx = st.session_state["chain_idx"]
    idx = max(0, min(idx, len(rows) - 1))

    col_prev, col_info, col_next = st.columns([1, 6, 1])
    with col_prev:
        if st.button("← Prev", disabled=(idx == 0)):
            st.session_state["chain_idx"] = idx - 1
            st.rerun()
    with col_next:
        if st.button("Next →", disabled=(idx == len(rows) - 1)):
            st.session_state["chain_idx"] = idx + 1
            st.rerun()
    with col_info:
        st.markdown(
            f"<div style='text-align:center; padding-top:6px'>"
            f"Message <b>{idx + 1}</b> of <b>{len(rows)}</b>"
            f"</div>",
            unsafe_allow_html=True,
        )

    row = rows.iloc[idx]
    st.title(f"{row['domain']} — Individual (participant {row['participant_id']})")

    render_message_card(row)
