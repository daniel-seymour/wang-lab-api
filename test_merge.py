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
    "cCRE_id": "EH38E1234567"
    }
    
    result = merge_variant_data("rs429358", myvariant_mock, gtex_mock)
    
    assert result["gene"] == "APOE"
    assert result["annotations"]["expression_GTEx"] == "high"
