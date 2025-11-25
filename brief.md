# 🧩 Take-Home Challenge: Genetic Data Explorer (API Integration & Minimal App)
**Duration:** 24 hours
**Primary Skills:** REST API design, data integration, lightweight app development (Streamlit or FastAPI)
**Cost Goal:** Zero or near-zero (public APIs only, no paid tools)

---

## 🧭 Context
Our lab builds data systems to organize and explore large-scale human genetics information.
For this assignment, you do **not** need prior biology knowledge — treat genetic data as structured fields (e.g., *variant ID*, *gene name*, *annotation score*).

The goal is to show that you can:
1. **Retrieve and combine data** from public REST APIs,
2. **Expose or visualize** that combined information through your own simple API or dashboard, and
3. **Document and reason** about your design clearly.

---

## 🎯 Goal
Create a **lightweight data explorer** or **REST API service** that retrieves and displays information about one or more *identifiers* (for example, “variant ID” or “gene symbol”).

You can use any one or more of the following example APIs (or mock data if offline):
- **FAVOR API** – Functional Annotation of Variants Online   https://docs.genohub.org/pagination
- **GTEx API** – Gene expression information  https://gtexportal.org/api/v2/redoc
- **AlphaGenome API** – Variant and functional annotations   https://github.com/google-deepmind/alphagenome

---

## 🧩 A. Starter Dataset
You can use any of the publications listed in the https://advp.niagads.org/publications instead of creating your own.  You can leverage search function in ADVP https://advp.niagads.org/search to get a list of relationship, e.g. a record of col "SNP" rs3865444 is within the "Locus" CD33 and you can show us how you get the API calls from the above.

Alternatively, you can use these mock examples below:


### 🧬 `favor_mock.json`
```json
{
  "variant_id": "rs429358",
  "gene": "APOE",
  "annotation_score": 0.97,
  "consequence": "missense_variant",
  "impact": "high"
}

🧩 FAVOR_mock.json
{
  "variant_id": "rs429358",
  "regulatory_feature": "enhancer",
  "tissue_activity": "brain",
  "cCRE_id": "EH38E1234567"
}
You can treat these files as if they came from real APIs.
If you prefer, you may replace them with live API calls later.

---

## 🧩 B. Core Requirements
Choose **one** of the two main paths:

### 🧠 Option A: REST API Developer
Build a minimal REST API using **FastAPI** (or Flask) that provides endpoints like:
- `GET /variant/{id}` → retrieves variant info from at least 2 APIs and merges results.
- `GET /gene/{symbol}` → optional secondary endpoint.
- Include at least one query parameter (e.g., `?tissue=brain` or `?fields=annotations`).

Example merged JSON output:
```json
{
  "variant": "rs429358",
  "gene": "APOE",
  "annotations": {
    "FAVOR_score": 0.97,
    "Enhancer": "brain_enhancer",
    "expression_GTEx": "high"
  }
}
```

### 💻 Option B: Interactive App Developer
Build a small Streamlit (or Gradio/Flask) app that:
- Has a search box (for variant/gene input).
- Fetches data from 2+ public APIs (or local mocks).
- Displays results in an interactive panel (tables, charts, or collapsible sections).
- Optionally allows export (JSON or CSV).



### 💡 Hints & Starter Guidance
1. Core Libraries
- requests, json, pandas for API calls and data handling
- fastapi, uvicorn for REST API apps
- streamlit or gradio for UI
- plotly or altair for charts (optional)
- pytest, requests-mock for testing (optional)

2. Example Setup
```bash
pip install fastapi uvicorn streamlit requests pandas
```

3. Minimal Workflow
a. Read mock data:
``` python
import json
favor = json.load(open("mock_data/favor_mock.json"))
GTEx = json.load(open("mock_data/GTEx_mock.json"))
```
b. Merge: Create a dictionary combining key fields (e.g., gene, impact, tissue).
c. Display: Print to console first → then return as JSON (FastAPI) or table (Streamlit).
d. Polish: Add error handling (“variant not found”) and a clean README.


### 💡 Bonus Features (Optional)
These bonus sections help assess strong API developers.

| Bonus                          | Description                                                                                            |
| ------------------------------ | ------------------------------------------------------------------------------------------------------ |
| 🧱 **API Design Quality**      | Use proper HTTP verbs, error codes, and status messages (e.g., 400 for invalid ID, 404 for not found). |
| 🧩 **Reusable Structure**      | Implement helper modules or dependency injection for external API clients.                             |
| 🧪 **Testing**                 | Add simple unit or integration tests using `pytest`.                                                   |
| 📦 **Dockerization**           | Provide a small `Dockerfile` or `docker-compose.yml`.                                                  |
| 🌐 **Documentation**           | Include Swagger/OpenAPI auto-docs (FastAPI) or a “Help” tab (Streamlit).                               |
| 🔄 **Caching / Rate Limiting** | Cache responses locally (e.g., `functools.lru_cache` or SQLite).                                       |
| 🔍 **Error Handling**          | Graceful fallback to mock data when API fails.                                                         |
| 🚀 **Deployment-ready**        | Show how it could be deployed on a free platform (Render, Hugging Face Spaces, etc.).                  |



### 📦 Deliverables
- GitHub repo containing:
    - Source code or notebook
    - A working REST API or app (python main.py or streamlit run app.py)
    - README.md including:
        - Which APIs you used or mocked
        - Example commands and screenshots
        - Brief explanation of your data model or visualization logic
        - Bonus features (if implemented)
    - (Optional) short demo video/gif
