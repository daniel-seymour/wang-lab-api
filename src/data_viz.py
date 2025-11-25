import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

def create_population_frequency_chart(favor_df: pd.DataFrame, variant_id: str) -> go.Figure:
    """Create population allele frequency bar chart"""

    pop_freq_data = {
        "African": favor_df["af_afr"].iloc[0],
        "Latino/Admixed American": favor_df["af_amr"].iloc[0],
        "East Asian": favor_df["af_eas"].iloc[0],
        "European (non-Finnish)": favor_df["af_nfe"].iloc[0],
        "Finnish": favor_df["af_fin"].iloc[0],
        "South Asian": favor_df["af_sas"].iloc[0],
        "Ashkenazi Jewish": favor_df["af_asj"].iloc[0],
        "Amish": favor_df["af_ami"].iloc[0],
        "Other": favor_df["af_oth"].iloc[0]
    }

    freq_df = pd.DataFrame({
        "Population": list(pop_freq_data.keys()),
        "Allele Frequency": list(pop_freq_data.values())
    })
    freq_df["Percentage (%)"] = freq_df["Allele Frequency"] * 100

    fig = px.bar(
        freq_df,
        x="Population",
        y="Percentage (%)",
        title=f"Allele Frequency of {variant_id} Across Populations",
        color="Percentage (%)",
        color_continuous_scale="Viridis",
        text="Percentage (%)"
    )

    fig.update_traces(texttemplate='%{text:.2f}%', textposition='outside')
    fig.update_layout(xaxis_tickangle=-45, showlegend=False, height=700)

    return fig


def create_functional_annotation_landscape(favor_df: pd.DataFrame, variant_id: str) -> go.Figure:
    """Create functional annotation visualization"""

    annotations = {
        "CADD Phred": ("cadd_phred", 0, 50),
        "GERP": ("gerp_rs", -12, 6),
        "PhyloP": ("phylop", -20, 10),
        "PhastCons": ("phastcons", 0, 1),
        "SIFT": ("sift_score", 0, 1),
        "PolyPhen2 (HDIV)": ("polyphen2_hdiv_score", 0, 1),
        "PolyPhen2 (HVAR)": ("polyphen2_hvar_score", 0, 1)
    }

    scores, labels = [], []
    for label, (col, min_val, max_val) in annotations.items():
        if col in favor_df.columns:
            value = favor_df[col].iloc[0]
            if pd.notna(value):
                normalized = ((value - min_val) / (max_val - min_val)) * 100
                scores.append(normalized)
                labels.append(f"{label}\n({value:.3f})")
            else:
                scores.append(0)
                labels.append(f"{label}\n(N/A)")

    fig = go.Figure(go.Bar(
        x=labels, y=scores,
        marker_color=scores,
        marker_colorscale='RdYlGn_r',
        text=[f"{s:.1f}%" for s in scores],
        textposition='outside'
    ))

    fig.update_layout(
        title=f"Functional Impact Scores for {variant_id}",
        xaxis_title="Annotation Type",
        yaxis_title="Normalized Score (0-100)",
        height=500,
        showlegend=False
    )

    return fig

def create_eqtl_heatmap(GTEx_data, variant_id):
    """Creates eQTL heatmap figure"""
    if not GTEx_data or "eqtl_results" not in GTEx_data:
        return None

    gtex_df = pd.DataFrame(GTEx_data["eqtl_results"])
    gtex_df["Tissue"] = gtex_df["tissueSiteDetailId"].str.replace("_", " ")

    heatmap_data = gtex_df.pivot_table(
        index="geneSymbol", columns="Tissue", values="nes", aggfunc="first"
    )
    pval_data = gtex_df.pivot_table(
        index="geneSymbol", columns="Tissue", values="pValue", aggfunc="first"
    )

    # Build annotations
    annotations = []
    for i, gene in enumerate(heatmap_data.index):
        row_annotations = []
        for j, tissue in enumerate(heatmap_data.columns):
            nes = heatmap_data.iloc[i, j]
            pval = pval_data.iloc[i, j]
            text = f"{nes:.3f}<br>p={pval:.2e}" if pd.notna(nes) else ""
            row_annotations.append(text)
        annotations.append(row_annotations)

    fig = go.Figure(data=go.Heatmap(
        z=heatmap_data.values,
        x=heatmap_data.columns,
        y=heatmap_data.index,
        colorscale="RdBu_r",
        zmid=0,
        text=annotations,
        texttemplate="%{text}",
        textfont={"size": 10},
        colorbar=dict(title="NES<br>(Effect Size)")
    ))

    fig.update_layout(
        title=f"eQTL Effects for {variant_id} Across Tissues",
        xaxis_title="Tissue",
        yaxis_title="Gene",
        height=400,
        xaxis=dict(tickangle=-45)
    )

    return fig


def create_functional_annotation_landscape(favor_df, variant_id):
    """Creates multi-layer functional annotation figure"""
    from plotly.subplots import make_subplots

    annotations_data = {
        "Conservation": {
            "GERP": favor_df["gerp_s"].iloc[0],
            "PhyloP (Mammal)": favor_df["mamphylop"].iloc[0],
            "PhyloP (Vertebrate)": favor_df["verphylop"].iloc[0]
        },
        "Epigenetics": {
            "H3K4me3 (Promoter)": favor_df["encodeh3k4me3_sum"].iloc[0],
            "H3K27ac (Enhancer)": favor_df["encodeh3k27ac_sum"].iloc[0],
            "H3K27me3 (Repression)": favor_df["encodeh3k27me3_sum"].iloc[0]
        },
        "Regulatory": {
            "TF Binding Sites": favor_df["remap_overlap_tf"].iloc[0],
            "Cell Lines (ChIP)": favor_df["remap_overlap_cl"].iloc[0]
        }
    }

    fig = make_subplots(
        rows=3, cols=1,
        subplot_titles=("Conservation Scores", "Epigenetic Marks", "Regulatory Features"),
        vertical_spacing=0.12,
        row_heights=[0.33, 0.33, 0.33]
    )

    # Conservation
    cons_df = pd.DataFrame({
        "Score": list(annotations_data["Conservation"].keys()),
        "Value": list(annotations_data["Conservation"].values())
    })
    fig.add_trace(go.Bar(x=cons_df["Score"], y=cons_df["Value"],
                         marker_color='lightblue', name="Conservation"),
                  row=1, col=1)

    # Epigenetics
    epi_df = pd.DataFrame({
        "Mark": list(annotations_data["Epigenetics"].keys()),
        "Signal": list(annotations_data["Epigenetics"].values())
    })
    fig.add_trace(go.Bar(x=epi_df["Mark"], y=epi_df["Signal"],
                         marker_color='lightcoral', name="Epigenetics"),
                  row=2, col=1)

    # Regulatory
    reg_df = pd.DataFrame({
        "Feature": list(annotations_data["Regulatory"].keys()),
        "Count": list(annotations_data["Regulatory"].values())
    })
    fig.add_trace(go.Bar(x=reg_df["Feature"], y=reg_df["Count"],
                         marker_color='lightgreen', name="Regulatory"),
                  row=3, col=1)

    fig.update_layout(height=700, showlegend=False,
                      title_text=f"Multi-Layer Functional Annotation: {variant_id}")

    return fig
