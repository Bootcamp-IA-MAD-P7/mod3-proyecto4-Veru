import sqlite3
from pathlib import Path

import streamlit as st

from src.db.database import init_db


st.set_page_config(page_title="Report", layout="wide")
st.title("Report & Gallery")

conn = init_db()
cur = conn.cursor()
cur.execute("SELECT * FROM videos ORDER BY id DESC")
videos = cur.fetchall()
conn.close()

if not videos:
    st.info("No videos analyzed yet.")
else:
    vid = st.selectbox("Select video", videos, format_func=lambda r: f"#{r['id']} {r['filename']}")
    if vid:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Duration", f"{vid['duration_sec']:.2f}s")
        c2.metric("Frames with logo", vid['frames_with_logo'])
        c3.metric("Logo time", f"{vid['logo_time_sec']:.2f}s")
        c4.metric("Percentage", f"{vid['percentage']:.2f}%")

        conn = init_db()
        cur = conn.cursor()
        cur.execute("SELECT * FROM detections WHERE video_id = ? ORDER BY frame_idx", (vid["id"],))
        dets = cur.fetchall()
        conn.close()

        st.subheader("Crops")
        if not dets:
            st.write("No detections.")
        else:
            imgs = [d["crop_path"] for d in dets if d["crop_path"] and Path(d["crop_path"]).exists()]
            if imgs:
                st.image(imgs, width=200)
            else:
                st.dataframe([dict(d) for d in dets])
