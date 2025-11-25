import pandas as pd
import json
from io import StringIO
from typing import Optional


def merge_variant_data(favor_data: list, gtex_data: dict, variant_id: str) -> dict:
    """
    Merge FAVOR annotation and GTEx eQTL data into a unified structure.

    Returns nested dict suitable for JSON export or flattening to CSV.
    """
    merged = {
        "variant_id": variant_id,
        "query_timestamp": pd.Timestamp.now().isoformat(),
        "favor_annotation": None,
        "gtex_eqtls": None,
        "summary": {}
    }

    # FAVOR data (single variant, take first element)
    if favor_data and len(favor_data) > 0:
        fav = favor_data[0]
        merged["favor_annotation"] = {
            "basic_info": {
                "rsid": fav.get("rsid"),
                "chromosome": fav.get("chromosome"),
                "position": fav.get("position"),
                "variant_vcf": fav.get("variant_vcf"),
                "gene": fav.get("genecode_comprehensive_info"),
                "consequence": fav.get("genecode_comprehensive_exonic_category"),
                "protein_change": fav.get("protein_variant"),
                "hgvsc": fav.get("hgvsc"),
                "hgvsp": fav.get("hgvsp"),
            },
            "pathogenicity_scores": {
                "cadd_phred": fav.get("cadd_phred"),
                "sift": {"score": fav.get("sift_val"), "prediction": fav.get("sift_cat")},
                "polyphen2": {"score": fav.get("polyphen_val"), "prediction": fav.get("polyphen_cat")},
                "alphamissense": {"score": fav.get("am_pathogenicity"), "prediction": fav.get("am_class")},
                "mutation_taster": fav.get("mutation_taster_score"),
                "gerp": fav.get("gerp_s"),
            },
            "population_frequencies": {
                "global": fav.get("af_total"),
                "african": fav.get("af_afr"),
                "european": fav.get("af_nfe"),
                "east_asian": fav.get("af_eas"),
                "south_asian": fav.get("af_sas"),
                "latino": fav.get("af_amr"),
                "ashkenazi": fav.get("af_asj"),
                "finnish": fav.get("af_fin"),
            },
            "clinical": {
                "clinvar_significance": fav.get("clnsig"),
                "clinvar_conditions": fav.get("clndn"),
                "review_status": fav.get("clnrevstat"),
            },
            "conservation": {
                "gerp_n": fav.get("gerp_n"),
                "gerp_s": fav.get("gerp_s"),
                "phylop_mammalian": fav.get("mamphylop"),
                "phylop_vertebrate": fav.get("verphylop"),
                "phastcons_mammalian": fav.get("mamphcons"),
            }
        }

        # Summary stats
        merged["summary"]["gene"] = fav.get("genecode_comprehensive_info")
        merged["summary"]["global_af"] = fav.get("af_total")
        merged["summary"]["clinvar"] = fav.get("clnsig")

    # GTEx eQTL data
    if gtex_data and "eqtl_results" in gtex_data:
        eqtls = gtex_data["eqtl_results"]
        merged["gtex_eqtls"] = {
            "total_associations": len(eqtls),
            "associations": [
                {
                    "gene": e.get("geneSymbol"),
                    "tissue": e.get("tissueSiteDetailId"),
                    "effect_size": e.get("nes"),
                    "p_value": e.get("pValue"),
                    "gencode_id": e.get("gencodeId"),
                }
                for e in eqtls
            ]
        }

        # Summary: most significant eQTL
        if eqtls:
            top_eqtl = min(eqtls, key=lambda x: x.get("pValue", 1))
            merged["summary"]["top_eqtl_gene"] = top_eqtl.get("geneSymbol")
            merged["summary"]["top_eqtl_tissue"] = top_eqtl.get("tissueSiteDetailId")
            merged["summary"]["top_eqtl_pvalue"] = top_eqtl.get("pValue")

    return merged


def to_flat_csv(merged_data: dict) -> pd.DataFrame:
    """
    Flatten nested merged data for CSV export.
    Returns one row per eQTL association (or one row if no eQTLs).
    """
    rows = []

    favor = merged_data.get("favor_annotation") or {}
    basic = favor.get("basic_info") or {}
    scores = favor.get("pathogenicity_scores") or {}
    freqs = favor.get("population_frequencies") or {}
    clinical = favor.get("clinical") or {}

    # Base row with FAVOR data
    base_row = {
        "variant_id": merged_data.get("variant_id"),
        "rsid": basic.get("rsid"),
        "chromosome": basic.get("chromosome"),
        "position": basic.get("position"),
        "gene": basic.get("gene"),
        "consequence": basic.get("consequence"),
        "protein_change": basic.get("protein_change"),
        "hgvsc": basic.get("hgvsc"),
        "hgvsp": basic.get("hgvsp"),
        # Scores
        "cadd_phred": scores.get("cadd_phred"),
        "sift_score": scores.get("sift", {}).get("score") if isinstance(scores.get("sift"), dict) else None,
        "sift_pred": scores.get("sift", {}).get("prediction") if isinstance(scores.get("sift"), dict) else None,
        "polyphen_score": scores.get("polyphen2", {}).get("score") if isinstance(scores.get("polyphen2"), dict) else None,
        "polyphen_pred": scores.get("polyphen2", {}).get("prediction") if isinstance(scores.get("polyphen2"), dict) else None,
        "alphamissense_score": scores.get("alphamissense", {}).get("score") if isinstance(scores.get("alphamissense"), dict) else None,
        "alphamissense_pred": scores.get("alphamissense", {}).get("prediction") if isinstance(scores.get("alphamissense"), dict) else None,
        "gerp": scores.get("gerp"),
        # Frequencies
        "af_global": freqs.get("global"),
        "af_african": freqs.get("african"),
        "af_european": freqs.get("european"),
        "af_east_asian": freqs.get("east_asian"),
        "af_south_asian": freqs.get("south_asian"),
        "af_latino": freqs.get("latino"),
        # Clinical
        "clinvar_significance": clinical.get("clinvar_significance"),
        "clinvar_conditions": clinical.get("clinvar_conditions"),
    }

    # Add eQTL rows (one per association) or single row if none
    gtex = merged_data.get("gtex_eqtls") or {}
    associations = gtex.get("associations") or []

    if associations:
        for eqtl in associations:
            row = base_row.copy()
            row["eqtl_gene"] = eqtl.get("gene")
            row["eqtl_tissue"] = eqtl.get("tissue")
            row["eqtl_effect_size"] = eqtl.get("effect_size")
            row["eqtl_pvalue"] = eqtl.get("p_value")
            rows.append(row)
    else:
        rows.append(base_row)

    return pd.DataFrame(rows)


def export_to_json(merged_data: dict) -> str:
    """Export merged data as formatted JSON string."""
    return json.dumps(merged_data, indent=2, default=str)


def export_to_csv(merged_data: dict) -> str:
    """Export flattened data as CSV string."""
    df = to_flat_csv(merged_data)
    return df.to_csv(index=False)
