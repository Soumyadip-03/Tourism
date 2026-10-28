# China Tourism Recommendation API

## Run locally on Windows

1. Install a compatible Python version.
2. Open PowerShell in this backend folder.
3. Create a virtual environment:

   py -m venv .venv

4. Activate it:

   .\.venv\Scripts\Activate.ps1

5. Install packages:

   python -m pip install --upgrade pip
   pip install -r requirements.txt

6. Start the API:

   uvicorn main:app --reload --host 127.0.0.1 --port 8000

7. Open http://127.0.0.1:8000/docs

Endpoints:
- GET /health
- GET /options
- POST /recommendations

Note: the SVM decision scores are not probabilities or guarantees of satisfaction.
Catalogue prices are dataset values, not live prices.
