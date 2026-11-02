import os
from pathlib import Path

import streamlit as st

from src.video.processor import process_video
from src.db.repository import save_video_result


st.set_page_config(page_title="Analyze", layout="wide")
st.title("Analyze Video")

uploaded = st.file_uploader("Upload video", type=["mp4", "webm", "mkv"])
model_path = st.text_input("Model", value="models/best.pt")
conf = st.slider("Confidence", 0.1, 0.9, 0.5, 0.05)
run = st.button("Run analysis")

if uploaded and run:
    uploads = Path("data/uploads")
    uploads.mkdir(parents=True, exist_ok=True)
    save_path = uploads / uploaded.name
    with open(save_path, "wb") as f:
        f.write(uploaded.getbuffer())
    with st.spinner("Processing..."):
        try:
            res = process_video(str(save_path), model_path=model_path, conf=conf)
            vid_id = save_video_result(res)
            st.success(f"Done. Video ID: {vid_id}")
            st.json(
                {
                    "duration_sec": res["duration_sec"],
                    "frames_with_logo": res["frames_with_logo"],
                    "logo_time_sec": res["logo_time_sec"],
                    "percentage": res["percentage"],
                }
            )
        except Exception as e:
            st.error(str(e))
