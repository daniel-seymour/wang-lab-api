## Installation

1. Clone the repository
2. Create a virtual environment: `python -m venv venv` NOT CORRECT
3. Activate it: `source venv/bin/activate` (macOS/Linux) or `venv\Scripts\activate` (Windows)
4. Install dependencies: `pip install -r requirements.txt`

## Running

[Add your specific commands here - e.g.:]
- Backend API: `uvicorn app:app --reload`
- Frontend: `streamlit run app.py` NOT CORRECT

README.md including:
        - Which APIs you used or mocked
        - Example commands and screenshots
        - Brief explanation of your data model or visualization logic
        - Bonus features (if implemented)
    - (Optional) short demo video/gif (provide link)


Final check:
clone repo and try again to see if

## Setup

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
