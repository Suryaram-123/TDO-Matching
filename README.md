# Store Verification AI — MVP

Evidence-first store verification for current, future, closed, replaced, and historical US business locations.

## What it does

Given store name + address, the app:
1. Searches Google Places API (New), including future-opening businesses.
2. Runs broad web searches for opening, closure, reopening, replacement, and historical evidence.
3. Uses an LLM when configured to classify evidence conservatively.
4. Stores an auditable JSON report in SQLite.
5. Shows clickable source URLs for the evidence it used.

Statuses:
- OPEN
- FUTURE_OPENING
- TEMPORARILY_CLOSED
- PERMANENTLY_CLOSED
- REPLACED
- HISTORICAL
- NOT_FOUND
- UNCERTAIN

## Setup

Python 3.11+ is recommended.

```powershell
py -m venv .venv
.venv\\Scripts\\activate
pip install -r requirements.txt
copy .env.example .env
streamlit run app.py
```

Set these in `.env`:

```text
GOOGLE_MAPS_API_KEY=your_key
TAVILY_API_KEY=optional_but_recommended
OPENAI_API_KEY=optional
OPENAI_MODEL=gpt-5-mini
DATABASE_PATH=store_verification.db
```

CSV batch input columns:

```text
store_name,address,city,state,postal_code,country
```

## Important production rule

Never let the model invent a URL. Every evidence URL must originate from a retrieved search result or API response. If no verified URL exists, record that explicitly.

Also review Google Maps Platform terms concerning storage, caching, attribution, and use of Places content before deploying this for company production.
