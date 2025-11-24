# Helper function to merge data from multiple APIs
def merge_variant_data(favor_data, regulatory_data):
    """Merge data from FAVOR and regulatory APIs"""
    favor_variant_id = favor_data.get("variant_id", "N/A")
    regulatory_variant_id = regulatory_data.get("variant_id", "N/A")
    
    # Check if variant IDs match
    if favor_variant_id != regulatory_variant_id:
        raise ValueError(
            f"Variant ID mismatch: FAVOR has '{favor_variant_id}' "
            f"but regulatory data has '{regulatory_variant_id}'"
        )
    
    return {
        "variant": favor_variant_id,
        "gene": favor_data.get("gene", "N/A"),
        "FAVOR_score": favor_data.get("annotation_score", "N/A"),
        "impact": favor_data.get("impact", "N/A"),
        "consequence": favor_data.get("consequence", "N/A"),
        "regulatory_feature": regulatory_data.get("regulatory_feature", "N/A"),
        "tissue_activity": regulatory_data.get("tissue_activity", "N/A"),
        "cCRE_id": regulatory_data.get("cCRE_id", "N/A")
    }