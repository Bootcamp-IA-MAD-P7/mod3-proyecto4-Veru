import streamlit as st

from src.db.repository import get_videos


st.set_page_config(page_title="History", layout="wide")
st.title("History")

try:
    rows = get_videos()
    if not rows:
        st.info("No history yet.")
    else:
        data = [dict(r) for r in rows]
        st.dataframe(data)
except Exception as e:
    st.error(str(e))
