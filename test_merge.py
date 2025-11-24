import pytest
from merge_api import merge_variant_data


def test_merge_with_complete_data():
    """Test merge when all fields present"""
    
    myvariant_mock = {
        "variant_id": "rs429358",
        "gene": "APOE",
        "annotation_score": 0.97,
        "consequence": "missense_variant",
        "impact": "high"
    }
    
    gtex_mock = {
        "variant_id": "rs429358",
        "regulatory_feature": "enhancer",
        "tissue_activity": "brain",
        "cCRE_id": "EH38E1234567",
    }

    result = merge_variant_data(myvariant_mock, gtex_mock)

    assert result["gene"] == "APOE"
    assert result["FAVOR_score"] == 0.97
    assert result["variant"] == "rs429358"
    assert result["regulatory_feature"] == "enhancer"


def test_variant_id_mismatch_raises():
    a = {"variant_id": "rs1"}
    b = {"variant_id": "rs2"}
    with pytest.raises(ValueError):
        merge_variant_data(a, b)
