from fetch_data import fetch_favor
import streamlit as st
import requests
import json
import pandas as pd
from merge_api import merge_variant_data

# Streamlit App
st.title("🧬 Genetic Variant Explorer")

st.write("Search for a variant or gene using the FAVOR, GTEx and AlphaGenome APIs")

# Input
variant_id = st.text_input("Enter Variant ID (e.g., rs429358):", "rs429358") 

if st.button("Search"):
    with st.spinner("Fetching data..."):
       favor_data = fetch_favor(variant_id)



