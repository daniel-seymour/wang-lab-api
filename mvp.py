import streamlit as st
import requests
import json
import pandas as pd
from merge_api import merge_variant_data 

# Streamlit App
st.title("🧬 Genetic Variant Explorer")

favor = json.load(open("mock_data/favor_mock.json"))
GTEx = json.load(open("mock_data/GTEx_mock.json"))

merged_data = merge_variant_data(favor, GTEx)

print("Merged Data:")
print(json.dumps(merged_data, indent=2))

df = pd.DataFrame([merged_data])


st.dataframe(df)


st.json(merged_data)