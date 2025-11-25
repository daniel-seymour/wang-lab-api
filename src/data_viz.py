import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

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


def create_functional_annotation_landscape(favor_df: pd.DataFrame, variant_id: str) -> go.Figure:
    # Correct column mappings based on actual FAVOR API response
    metrics = {
        "CADD": {
            "col": "cadd_phred",
            "thresholds": [(0, "Benign"), (15, "Uncertain"), (20, "Likely Pathogenic"), (30, "Pathogenic")],
            "higher_worse": True,
            "max_val": 40
        },
        "SIFT": {
            "col": "sift_val",  # NOT sift_score
            "thresholds": [(0, "Damaging"), (0.05, "Possibly Damaging"), (0.5, "Tolerated")],
            "higher_worse": False,  # Lower = worse for SIFT
            "max_val": 1
        },
        "PolyPhen2": {
            "col": "polyphen_val",  # Use polyphen_val, not polyphen2_hdiv_score
            "thresholds": [(0, "Benign"), (0.45, "Possibly Damaging"), (0.85, "Probably Damaging")],
            "higher_worse": True,
            "max_val": 1
        },
        "AlphaMissense": {
            "col": "am_pathogenicity",  # String in API, needs conversion
            "thresholds": [(0, "Likely Benign"), (0.34, "Uncertain"), (0.564, "Likely Pathogenic")],
            "higher_worse": True,
            "max_val": 1
        },
        "GERP++": {
            "col": "gerp_s",  # NOT gerp_rs
            "thresholds": [(-12, "Not Conserved"), (2, "Conserved"), (4, "Highly Conserved")],
            "higher_worse": True,
            "max_val": 6,
            "min_val": -12
        },
        "MutationTaster": {
            "col": "mutation_taster_score",
            "thresholds": [(0, "Polymorphism"), (0.5, "Uncertain"), (0.95, "Disease Causing")],
            "higher_worse": True,
            "max_val": 1
        },
    }

    data = []

    for name, config in metrics.items():
        col = config["col"]
        if col not in favor_df.columns:
            continue

        raw_value = favor_df[col].iloc[0]

        # Handle missing/null
        if pd.isna(raw_value):
            continue

        # Handle string->float (AlphaMissense comes as string)
        try:
            value = float(raw_value)
        except (ValueError, TypeError):
            continue

        # Determine interpretation and color
        thresholds = config["thresholds"]
        if config["higher_worse"]:
            # Find highest threshold that value exceeds
            interp = thresholds[0][1]
            for thresh_val, thresh_label in thresholds:
                if value >= thresh_val:
                    interp = thresh_label
        else:
            # SIFT: lower is worse
            interp = thresholds[-1][1]  # Default to best
            for thresh_val, thresh_label in thresholds:
                if value <= thresh_val:
                    interp = thresh_label
                    break

        # Color mapping
        color_map = {
            "Benign": "#4caf50",
            "Tolerated": "#4caf50",
            "Likely Benign": "#4caf50",
            "Not Conserved": "#4caf50",
            "Polymorphism": "#4caf50",
            "Uncertain": "#ff9800",
            "Possibly Damaging": "#ff9800",
            "Conserved": "#ff9800",
            "Damaging": "#d32f2f",
            "Probably Damaging": "#d32f2f",
            "Likely Pathogenic": "#d32f2f",
            "Pathogenic": "#d32f2f",
            "Highly Conserved": "#2196f3",  # Blue for conservation (not pathogenic per se)
            "Disease Causing": "#d32f2f",
        }
        color = color_map.get(interp, "#9e9e9e")

        data.append({
            "Metric": name,
            "Score": value,
            "Interpretation": interp,
            "Color": color,
            "MaxVal": config["max_val"],
            "MinVal": config.get("min_val", 0)
        })

    if not data:
        fig = go.Figure()
        fig.add_annotation(
            text="No pathogenicity scores available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False, font=dict(size=16)
        )
        fig.update_layout(height=200)
        return fig

    df = pd.DataFrame(data)

    fig = go.Figure()

    for _, row in df.iterrows():
        # Normalize score for display (handle different scales)
        min_val = row["MinVal"]
        max_val = row["MaxVal"]
        normalized = (row["Score"] - min_val) / (max_val - min_val)

        # Ensure minimum bar visibility for very small/zero values
        display_width = max(normalized, 0.02)

        fig.add_trace(go.Bar(
            y=[row["Metric"]],
            x=[display_width],
            orientation='h',
            marker_color=row["Color"],
            text=f'{row["Score"]:.3f} ({row["Interpretation"]})',
            textposition='outside',
            textfont=dict(size=11),
            name=row["Metric"],
            showlegend=False,
            hovertemplate=(
                f"<b>{row['Metric']}</b><br>"
                f"Score: {row['Score']:.4f}<br>"
                f"Classification: {row['Interpretation']}<extra></extra>"
            )
        ))

    fig.update_layout(
        title=dict(
            text=f"Pathogenicity Assessment: {variant_id}",
            x=0.5,
            xanchor='center',
            font=dict(size=16)
        ),
        xaxis=dict(
            title="Normalized Score",
            range=[0, 1.3],  # Extra space for labels
            tickformat=".0%"
        ),
        yaxis=dict(title="", automargin=True),
        height=max(350, len(data) * 60),
        template="plotly_dark",  # Match your dark theme
        margin=dict(l=120, r=180, t=60, b=50),
        bargap=0.3
    )

    return fig
