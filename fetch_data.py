
def fetch_favor(variant_id: str) -> Optional[Dict[str, Any]]:
    """Fetch functional annotation from FAVOR API"""
    try:
        # FAVOR API endpoint for variant annotation
        url = "https://favor.genohub.org/api/v1/variant"
        params = {"variant": variant_id}
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        st.warning(f"FAVOR API unavailable: {e}")
    return None

# def fetch_gtex(gene_symbol: str) -> Optional[Dict[str, Any]]:
#     """Fetch gene expression data from GTEx API"""
#     try:
#         # GTEx median expression by tissue
#         url = f"https://gtexportal.org/api/v2/expression/medianGeneExpression"
#         params = {
#             "geneId": gene_symbol,
#             "datasetId": "gtex_v8"
#         }
#         response = requests.get(url, params=params, timeout=10)
#         if response.status_code == 200:
#             return response.json()
#     except Exception as e:
#         st.warning(f"GTEx API error: {e}")
#     return None


# def extract_core_fields(favor_data: Dict, 
#                        gtex_data: Dict) -> pd.DataFrame:
#     """Extract and merge key fields from all APIs"""
    
#     core_fields = []
    
#     # Extract from FAVOR
#     if favor_data:
#         core_fields.append({
#             "Source": "FAVOR",
#             "Gene": favor_data.get('gene_name'),
#             "Functional Score": favor_data.get('CADD_phred', 'N/A'),
#             "Conservation": favor_data.get('phyloP100way', 'N/A'),
#             "Impact": favor_data.get('consequence', 'unknown')
#         })
    
#     # Extract from AlphaGenome
#     if alpha_data:
#         core_fields.append({
#             "Source": "AlphaGenome",
#             "Pathogenicity Score": f"{alpha_data['pathogenicity_score']:.2f}",
#             "Confidence": f"{alpha_data['confidence']:.2f}",
#             "Predicted Impact": alpha_data['predicted_impact'],
#             "Molecular Consequence": alpha_data['molecular_consequence']
#         })
    
#     return pd.DataFrame(core_fields) if core_fields else pd.DataFrame()