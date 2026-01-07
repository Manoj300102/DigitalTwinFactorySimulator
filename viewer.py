import streamlit as st

st.set_page_config(page_title="3D Factory View", layout="wide")

st.title("🛠 Drilling Machine Image")

st.image(
    "static/images/drilling_machine.png",
    caption="Drilling Machine Model",
    use_container_width=True
)