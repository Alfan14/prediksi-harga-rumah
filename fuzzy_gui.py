import streamlit as st
from fuzzy_core import fuzzy_predict

st.title("Prediksi Harga Rumah Madiun (Fuzzy Sugeno)")

land = st.number_input("Luas Tanah (m²)", min_value=30, max_value=500)
bang = st.number_input("Luas Bangunan (m²)", min_value=20, max_value=400)

if st.button("Prediksi Harga"):
    result = fuzzy_predict(land, bang)
    st.success(f"Estimasi Harga: Rp {int(result):,}")
