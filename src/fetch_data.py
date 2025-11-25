from typing import Optional, Dict, Any
import requests
import streamlit as st


def fetch_favor(variant_id: str) -> Optional[Dict[str, Any]]:
    """Fetch functional annotation from FAVOR API"""
    try:
        url = f"https://api.genohub.org/v1/rsids/{variant_id}"  # variant_id in path

        st.write(f"Requesting {url}")

        response = requests.get(url, timeout=10)  # No params needed

        st.write(f"Status code: {response.status_code}")

        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"FAVOR API returned status {response.status_code}")
            return {"error": f"Status {response.status_code}", "response": response.text}

    except Exception as e:
        st.error(f"FAVOR API error: {e}")
        return {"error": str(e)}

GTEX_BASE = "https://gtexportal.org/api/v2"

def fetch_gtex(rsid: str) -> Optional[Dict[str, Any]]:
    """
    Fetch GTEx regulatory (eQTL) data for a given rsID.
    """

    # 1. First lookup: convert rsID → variantId
    variant_lookup_url = f"{GTEX_BASE}/dataset/variant"
    params = {"snpId": rsid, "datasetId": "gtex_v8"}

    st.write(f"**GTEx Step 1:** Requesting {variant_lookup_url}")
    st.write(f"Params: {params}")

    try:
        resp = requests.get(variant_lookup_url, params=params)
        st.write(f"Status code: {resp.status_code}")

        if resp.status_code != 200:
            return {"error": f"GTEx lookup failed with {resp.status_code}"}

        variant_json = resp.json()

        if not variant_json.get("data"):
            return {"error": f"rsID {rsid} not found in GTEx v8"}

        variant_id = variant_json["data"][0]["variantId"]
        st.write(f"Found variantId: {variant_id}")

    except Exception as e:
        return {"error": f"Error during GTEx variant lookup: {e}"}

    # 2. Second call: get eQTL associations
    eqtl_url = f"{GTEX_BASE}/association/singleTissueEqtl"
    eqtl_params = {
        "variantId": variant_id,
        "datasetId": "gtex_v8",
        "page": 0,
        "itemsPerPage": 250,
    }

    st.write(f"**GTEx Step 2:** Requesting {eqtl_url}")
    st.write(f"Params: {eqtl_params}")

    try:
        eqtl_resp = requests.get(eqtl_url, params=eqtl_params)
        st.write(f"Status code: {eqtl_resp.status_code}")

        if eqtl_resp.status_code != 200:
            return {"error": f"GTEx eQTL fetch failed with {eqtl_resp.status_code}"}

        eqtl_json = eqtl_resp.json()

        return {
            "rsid": rsid,
            "variantId": variant_id,
            "eqtl_results": eqtl_json.get("data", []),
            "paging": eqtl_json.get("paging_info", {}),
        }

    except Exception as e:
        return {"error": f"Error during GTEx eQTL fetch: {e}"}

def fetch_alphagenome(chromosome: str, position: str, ref: str, alt: str, gene: str) -> Optional[Dict[str, Any]]:
    """
    Fetch AlphaGenome/AlphaMissense data

    Note: Replace with actual AlphaGenome API endpoint
    """
    try:
        # Example API structure - adjust based on actual AlphaGenome API
        url = "https://api.alphagenome.org/v1/variant"  # Replace with real endpoint

        params = {
            "chromosome": chromosome,
            "position": position,
            "reference": ref,
            "alternate": alt,
            "gene": gene
        }

        st.write(f"**AlphaGenome:** Requesting {url}")
        st.write(f"Params: {params}")

        response = requests.get(url, params=params, timeout=10)
        st.write(f"Status code: {response.status_code}")

        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"AlphaGenome API returned status {response.status_code}")
            return None

    except Exception as e:
        st.error(f"AlphaGenome API error: {e}")
        return None
