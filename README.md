## How to run the app
1. Clone the repository
2. Create a virtual environment:
```bash
   uv venv
   source .venv/bin/activate  # or `.venv\Scripts\activate` on Windows
```
3. Install dependencies:
```bash
   uv pip install -r requirements.txt
   uv pip install -e .
```
4. Run tests:
```bash
   pytest
```
```

### With uv (recommended - faster):
```bash
git clone
cd wang-lab-api
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt
streamlit run app.py
```

### With standard Python:
```bash
git clone
cd wang-lab-api
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```




- Optionally allows export (JSON or CSV).
d. Polish: Add error handling (“variant not found”) and a clean README.
Deploy with link in README
README.md including:
        - Which APIs you used or mocked
        - Example commands and screenshots
        - Brief explanation of your data model or visualization logic
        - Bonus features (if implemented)


README.md including:
        - Which APIs you used or mocked - Favor API GET Variant and GTX
        - Example commands and screenshots
        - Brief explanation of your data model or visualization logic - go from 🌍 Global Population Allele Frequencies
to 🧬 Functional Annotation Landscape to 🔬 eQTL Effect Heatmap, what's pattern here? More narrowing?
        - Bonus features are the Help tab, the export option, 

