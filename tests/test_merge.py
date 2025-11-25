import pytest
from merge_api import merge_variant_data, export_to_json, export_to_csv


# ============================================================
# FIXTURES - Realistic mock data matching actual API responses
# ============================================================

@pytest.fixture
def favor_mock():
    """Minimal FAVOR response with key fields"""
    return [{
        "rsid": "rs429358",
        "chromosome": "19",
        "position": "44908684",
        "variant_vcf": "19-44908684-T-C",
        "genecode_comprehensive_info": "APOE",
        "genecode_comprehensive_exonic_category": "nonsynonymous SNV",
        "protein_variant": "C130R",
        "hgvsc": "ENST00000252486.8:c.388T>C",
        "hgvsp": "ENSP00000252486.3:p.Cys130Arg",
        "cadd_phred": 17.93,
        "sift_val": 1,
        "sift_cat": "tolerated",
        "polyphen_val": 0.001,
        "polyphen_cat": "benign",
        "am_pathogenicity": "0.0365",
        "am_class": "likely_benign",
        "gerp_s": 6.84,
        "af_total": 0.159604,
        "af_afr": 0.213646,
        "af_nfe": 0.137516,
        "af_eas": 0.0965251,
        "af_sas": 0.114098,
        "af_amr": 0.110485,
        "clnsig": "Conflicting_interpretations_of_pathogenicity",
        "clndn": "Alzheimer_disease",
        "clnrevstat": "criteria_provided,_conflicting_interpretations",
    }]


@pytest.fixture
def gtex_mock():
    """Minimal GTEx response with eQTL results"""
    return {
        "rsid": "rs429358",
        "variantId": "chr19_44908684_T_C_b38",
        "eqtl_results": [
            {
                "snpId": "rs429358",
                "geneSymbol": "APOC1",
                "tissueSiteDetailId": "Esophagus_Mucosa",
                "pValue": 0.0000231811,
                "nes": -0.283485,
                "gencodeId": "ENSG00000130208.9",
            },
            {
                "snpId": "rs429358",
                "geneSymbol": "APOC1",
                "tissueSiteDetailId": "Adrenal_Gland",
                "pValue": 0.000047508,
                "nes": -0.364356,
                "gencodeId": "ENSG00000130208.9",
            },
        ],
        "paging": {"totalNumberOfItems": 2},
    }


# ============================================================
# MERGE FUNCTION TESTS
# ============================================================

class TestMergeVariantData:

    def test_merge_complete_data(self, favor_mock, gtex_mock):
        """Merge succeeds with both data sources present"""
        result = merge_variant_data(favor_mock, gtex_mock, "rs429358")

        # Check structure
        assert result["variant_id"] == "rs429358"
        assert "favor_annotation" in result
        assert "gtex_eqtls" in result
        assert "summary" in result

    def test_favor_fields_extracted(self, favor_mock, gtex_mock):
        """FAVOR annotation fields correctly nested"""
        result = merge_variant_data(favor_mock, gtex_mock, "rs429358")
        favor = result["favor_annotation"]

        # Basic info
        assert favor["basic_info"]["gene"] == "APOE"
        assert favor["basic_info"]["protein_change"] == "C130R"
        assert favor["basic_info"]["chromosome"] == "19"

        # Pathogenicity scores
        assert favor["pathogenicity_scores"]["cadd_phred"] == 17.93
        assert favor["pathogenicity_scores"]["sift"]["score"] == 1
        assert favor["pathogenicity_scores"]["sift"]["prediction"] == "tolerated"

        # Population frequencies
        assert favor["population_frequencies"]["global"] == pytest.approx(0.159604)
        assert favor["population_frequencies"]["african"] == pytest.approx(0.213646)

    def test_gtex_eqtls_extracted(self, favor_mock, gtex_mock):
        """GTEx eQTL associations correctly extracted"""
        result = merge_variant_data(favor_mock, gtex_mock, "rs429358")
        gtex = result["gtex_eqtls"]

        assert gtex["total_associations"] == 2
        assert len(gtex["associations"]) == 2

        first = gtex["associations"][0]
        assert first["gene"] == "APOC1"
        assert first["tissue"] == "Esophagus_Mucosa"
        assert first["effect_size"] == pytest.approx(-0.283485)

    def test_summary_populated(self, favor_mock, gtex_mock):
        """Summary contains key fields from both sources"""
        result = merge_variant_data(favor_mock, gtex_mock, "rs429358")
        summary = result["summary"]

        assert summary["gene"] == "APOE"
        assert summary["global_af"] == pytest.approx(0.159604)
        assert summary["top_eqtl_gene"] == "APOC1"
        assert summary["top_eqtl_pvalue"] == pytest.approx(0.0000231811)

    def test_favor_only(self, favor_mock):
        """Merge works with FAVOR data only (no GTEx)"""
        result = merge_variant_data(favor_mock, None, "rs429358")

        assert result["favor_annotation"] is not None
        assert result["gtex_eqtls"] is None
        assert result["summary"]["gene"] == "APOE"

    def test_gtex_only(self, gtex_mock):
        """Merge works with GTEx data only (no FAVOR)"""
        result = merge_variant_data(None, gtex_mock, "rs429358")

        assert result["favor_annotation"] is None
        assert result["gtex_eqtls"]["total_associations"] == 2

    def test_empty_favor_list(self, gtex_mock):
        """Handles empty FAVOR list gracefully"""
        result = merge_variant_data([], gtex_mock, "rs429358")

        assert result["favor_annotation"] is None
        assert result["gtex_eqtls"] is not None

    def test_empty_gtex_results(self, favor_mock):
        """Handles GTEx with no eQTL hits"""
        gtex_empty = {"rsid": "rs429358", "eqtl_results": []}
        result = merge_variant_data(favor_mock, gtex_empty, "rs429358")

        assert result["gtex_eqtls"]["total_associations"] == 0
        assert "top_eqtl_gene" not in result["summary"]

    def test_both_none(self):
        """Returns valid structure even with no data"""
        result = merge_variant_data(None, None, "rs429358")

        assert result["variant_id"] == "rs429358"
        assert result["favor_annotation"] is None
        assert result["gtex_eqtls"] is None


# ============================================================
# EXPORT FUNCTION TESTS
# ============================================================

class TestExportFunctions:

    def test_export_json_valid(self, favor_mock, gtex_mock):
        """JSON export produces valid JSON string"""
        import json

        merged = merge_variant_data(favor_mock, gtex_mock, "rs429358")
        json_str = export_to_json(merged)

        # Should be parseable
        parsed = json.loads(json_str)
        assert parsed["variant_id"] == "rs429358"

    def test_export_csv_rows(self, favor_mock, gtex_mock):
        """CSV has one row per eQTL association"""
        merged = merge_variant_data(favor_mock, gtex_mock, "rs429358")
        csv_str = export_to_csv(merged)

        lines = csv_str.strip().split("\n")
        assert len(lines) == 3  # header + 2 eQTL rows

    def test_export_csv_columns(self, favor_mock, gtex_mock):
        """CSV contains expected columns"""
        merged = merge_variant_data(favor_mock, gtex_mock, "rs429358")
        csv_str = export_to_csv(merged)

        header = csv_str.split("\n")[0]
        assert "variant_id" in header
        assert "cadd_phred" in header
        assert "eqtl_gene" in header
        assert "eqtl_tissue" in header

    def test_export_csv_no_eqtls(self, favor_mock):
        """CSV with no eQTLs produces single row"""
        merged = merge_variant_data(favor_mock, None, "rs429358")
        csv_str = export_to_csv(merged)

        lines = csv_str.strip().split("\n")
        assert len(lines) == 2  # header + 1 row


# ============================================================
# EDGE CASES
# ============================================================

class TestEdgeCases:

    def test_missing_optional_fields(self):
        """Handles FAVOR response missing optional fields"""
        minimal_favor = [{
            "rsid": "rs123",
            "chromosome": "1",
            "position": "12345",
        }]

        result = merge_variant_data(minimal_favor, None, "rs123")

        # Should not raise, missing fields become None
        assert result["favor_annotation"]["basic_info"]["rsid"] == "rs123"
        assert result["favor_annotation"]["pathogenicity_scores"]["cadd_phred"] is None

    def test_alphamissense_string_conversion(self):
        """AlphaMissense score (string in API) handled correctly"""
        favor = [{"am_pathogenicity": "0.0365", "am_class": "likely_benign"}]

        result = merge_variant_data(favor, None, "rs123")

        # Should remain as string (conversion happens in viz, not merge)
        assert result["favor_annotation"]["pathogenicity_scores"]["alphamissense"]["score"] == "0.0365"
