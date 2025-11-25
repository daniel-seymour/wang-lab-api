import streamlit as st
import requests
import json
import pandas as pd
from fetch_data import fetch_favor, fetch_gtex
from merge_api import merge_variant_data
from dotenv import load_dotenv
import os
import plotly.express as px
from src.data_viz import create_population_frequency_chart, create_eqtl_heatmap, create_functional_annotation_landscape

st.set_page_config(layout="wide")

favor_columns_to_show = [
    "rsid",
    "chromosome",
    "position",
    "variant_vcf",
    "genecode_comprehensive_info",
    "genecode_comprehensive_exonic_category",
    "protein_variant",
    "cadd_phred",
    "am_class",
    "clnsig",
    "af_total",
    "sift_cat",
    "polyphen_cat"
]

GTEx_columns_to_show = [
    "snpId",
    "geneSymbol",
    "tissueSiteDetailId",
    "pValue",
    "nes"
]

st.title("🧬 Genetic Variant Explorer")

# Create tabs
tab1, tab2 = st.tabs(["🔍 Search", "❓ Help"])

with tab1:
    st.write("Search for a variant (rsID) using the FAVOR, GTEx and AlphaGenome APIs")

    variant_id = st.text_input("Enter rsID (e.g., rs429358):", "rs429358")

    if st.button("Search"):
    # ========== FETCH ALL DATA FIRST ==========
        with st.expander("🔧 API Request Details (Click to expand)", expanded=False):
            with st.spinner("Fetching data from all sources..."):
                # Fetch FAVOR
                favor_data = fetch_favor(variant_id)

                # Show raw FAVOR data
                if favor_data:
                    st.markdown("**FAVOR Raw Response:**")
                    st.json(favor_data)  # Pretty-prints JSON

                # Fetch GTEx
                GTEx_data = fetch_gtex(variant_id)

                # Show raw GTEx data
                if GTEx_data:
                    st.markdown("**GTEx Raw Response:**")
                    st.json(GTEx_data)  # Pretty-prints JSON

            st.success("✅ Data fetching complete!")

        # ========== DISPLAY RAW DATA TABLES ==========

        # FAVOR Table
        if favor_data:
            favor_df = pd.DataFrame(favor_data)
            with st.expander("📘 FAVOR Annotation Table (Click to expand)"):
                st.dataframe(favor_df[favor_columns_to_show])
        else:
            st.warning("⚠️ No FAVOR results found.")

        # GTEx Table (right after FAVOR)
        if GTEx_data and "eqtl_results" in GTEx_data:
            gtex_df = pd.DataFrame(GTEx_data["eqtl_results"])
            with st.expander("🧫 GTEx eQTL Results Table (Click to expand)"):
                st.dataframe(gtex_df[GTEx_columns_to_show])
        else:
            st.warning("⚠️ No GTEx eQTL results found.")

        # ========== DISPLAY VISUALIZATIONS ==========

        if favor_data:
            st.subheader("Data Visualizations")

            st.markdown("#### 🌍 Global Population Allele Frequencies")
            fig1 = create_population_frequency_chart(favor_df, variant_id)
            st.plotly_chart(fig1, use_container_width=True)

            st.markdown("#### 🧬 Functional Annotation Landscape")
            fig2 = create_functional_annotation_landscape(favor_df, variant_id)
            st.plotly_chart(fig2, use_container_width=True)

        # eQTL Heatmap
        if GTEx_data:
            fig = create_eqtl_heatmap(GTEx_data, variant_id)
            if fig:
                st.markdown("#### 🔬 eQTL Effect Heatmap")
                st.plotly_chart(fig, use_container_width=True)


with tab2:
    st.header("Help & Documentation")
    st.markdown("""
    ### What is this tool?
    This app allows you to explore genetic variants using multiple databases:
    - **FAVOR**: Functional annotation and pathogenicity predictions
    - **GTEx**: Expression quantitative trait loci (eQTL) data

    ### How to use:
    1. Enter an rsID (e.g., rs429358 for APOE ε4)
    2. Click "Search"
    3. View functional annotations and population frequencies

    ### Understanding the results:
    - **CADD score**: Higher = more deleterious (>20 is pathogenic)
    - **Allele frequency**: % of population carrying this variant
    - **eQTL**: Variants affecting gene expression

    ### Example variants:
    - `rs429358` - APOE ε4 (Alzheimer's risk)
    - `rs7412` - APOE ε2 (protective)
    """)
