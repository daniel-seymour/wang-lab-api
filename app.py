import streamlit as st
import requests
import json

# Helper function to merge data from multiple APIs
def merge_variant_data(variant_id, myvariant_data, ensembl_data):
    """Merge data from multiple APIs into comprehensive view"""
    return {
        "variant_id": variant_id,
        
        # Gene information
        "gene": myvariant_data.get("cadd", {}).get("gene", {}).get("genename", "N/A"),
        
        # Impact/consequence
        "clinical_significance": myvariant_data.get("clinvar", {}).get("rcv", {}).get("clinical_significance", "N/A"),
        "cadd_score": myvariant_data.get("cadd", {}).get("phred", "N/A"),  # deleteriousness score
        
        # Location
        "chromosome": ensembl_data.get("mappings", [{}])[0].get("seq_region_name", "N/A") if ensembl_data.get("mappings") else "N/A",
        "position": ensembl_data.get("mappings", [{}])[0].get("start", "N/A") if ensembl_data.get("mappings") else "N/A",
        
        # Additional context
        "consequence_type": ensembl_data.get("most_severe_consequence", "N/A"),
        "minor_allele_freq": ensembl_data.get("MAF", "N/A"),
        
        # Metadata
        "data_sources": ["MyVariant.info", "Ensembl"]
    }

# Streamlit App
st.title("🧬 Genetic Variant Explorer")

st.write("Search for genetic variants using multiple public APIs")

# Input
variant_id = st.text_input("Enter Variant ID (e.g., rs429358):", "rs429358")

if st.button("Search"):
    with st.spinner("Fetching data..."):
        
        # API 1: MyVariant.info
        st.subheader("📊 MyVariant.info Data")
        try:
            url1 = f"https://myvariant.info/v1/variant/{variant_id}"
            response1 = requests.get(url1)
            
            if response1.status_code == 200:
                data1 = response1.json()
                st.json(data1)
            else:
                st.error(f"MyVariant API returned status {response1.status_code}")
        except Exception as e:
            st.error(f"Error fetching from MyVariant: {e}")
        
