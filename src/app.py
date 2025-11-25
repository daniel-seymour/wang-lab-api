import streamlit as st
import pandas as pd
import plotly.express as px
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from data_viz import create_population_frequency_chart, create_eqtl_heatmap, create_functional_annotation_landscape
from fetch_data import fetch_favor, fetch_gtex
from merge_api import merge_variant_data, export_to_json, export_to_csv



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
    st.write("Search for a variant and recieve data vizualisations from the FAVOR and GTEx databases.")

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

        if favor_data or GTEx_data:
            st.subheader("📥 Export Data")
            merged = merge_variant_data(favor_data, GTEx_data, variant_id)

            col1, col2 = st.columns(2)
            with col1:
                st.download_button("⬇️ JSON", export_to_json(merged),
                                f"{variant_id}.json", "application/json")
            with col2:
                st.download_button("⬇️ CSV", export_to_csv(merged),
                                f"{variant_id}.csv", "text/csv")

            st.caption("💡 CSV uses tidy format: one row per eQTL association, with annotation data repeated. "
                    "JSON preserves the nested structure.")


with tab2:
    st.header("Help & Documentation")

    st.markdown("""
    ### What is this tool?
    A variant annotation explorer that integrates multiple genomics databases to provide
    functional predictions, population frequencies, and expression data for genetic variants.

    ---

    ### Data Sources

    | Database | Description | Key Fields |
    |----------|-------------|------------|
    | **[FAVOR](https://favor.genohub.org/)** | Functional Annotation of Variants Online Resource from Harvard/WUSTL. Aggregates 50+ annotation tracks including pathogenicity predictors, conservation scores, and population frequencies from gnomAD. | CADD, SIFT, PolyPhen2, AlphaMissense, ClinVar |
    | **[GTEx](https://gtexportal.org/)** | Genotype-Tissue Expression project (NIH). Maps expression quantitative trait loci (eQTLs) across 54 human tissues from ~1000 donors. | Tissue, effect size (NES), p-value |

    ---

    ### Visualizations

    **Population Allele Frequencies:**
    Compares variant frequency across global populations (gnomAD). Large differences may indicate
    population-specific selection or drift. Common variants (>1%) are unlikely to cause severe
    Mendelian disease.

    **Pathogenicity Assessment:**
    Normalized scores from multiple predictors. Note that predictors measure different things:
    - **SIFT/PolyPhen2/AlphaMissense**: Protein structure/function impact
    - **GERP++/MutationTaster**: Evolutionary conservation
    - **CADD**: Integrative deleteriousness score

    ⚠️ *Discordant predictions are common and biologically meaningful.* A variant can be
    "tolerated" by structure predictors yet highly conserved—this pattern often indicates
    functional effects beyond simple protein disruption (e.g., altered binding affinity,
    tissue-specific regulation).

    **🔬 eQTL Heatmap**
    Shows tissues where the variant significantly affects gene expression. Normalized Effect
    Size (NES) indicates direction: positive = increased expression with alt allele,
    negative = decreased.

    ---

    ### Interpreting Key Scores

    | Score | Benign | Uncertain | Pathogenic |
    |-------|--------|-----------|------------|
    | CADD (phred) | <15 | 15-20 | >20 |
    | SIFT | >0.05 | 0.05 | <0.05 |
    | PolyPhen2 | <0.45 | 0.45-0.85 | >0.85 |
    | AlphaMissense | <0.34 | 0.34-0.56 | >0.56 |
    | GERP++ | <2 | 2-4 | >4 (conserved) |

    ---

    ### Export Formats

    | Format | Structure | Best For |
    |--------|-----------|----------|
    | **JSON** | Nested hierarchy | Programmatic access, preserves all relationships |
    | **CSV** | Tidy/long format (1 row per eQTL) | Excel, R, pandas—annotation columns repeat per eQTL |

    ---

    ### Example Variants

    | rsID | Gene | Clinical Relevance |
    |------|------|-------------------|
    | `rs429358` | APOE | ε4 allele — strongest genetic risk factor for Alzheimer's |
    | `rs7412` | APOE | ε2 allele — protective against Alzheimer's |
    | `rs1801133` | MTHFR | C677T — folate metabolism, homocysteine levels |
    | `rs334` | HBB | Sickle cell variant (HbS) |
    | `rs12913832` | HERC2 | Blue/brown eye color determinant |

    ---
    """)
