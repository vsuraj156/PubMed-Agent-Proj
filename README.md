# PubMed Research Agent

**Live demo: [pub-med-agent-proj.vercel.app](https://pub-med-agent-proj.vercel.app/)**

An AI-powered clinical research assistant that searches PubMed and synthesizes evidence-based summaries in response to medical questions.

## How it works

The agent takes a clinical question, decides which PubMed search tools to use, iteratively queries the literature, and returns a structured research report with citations.

**Tools available to the agent:**
- `search_pubmed` — general medical literature search
- `search_clinical_guidelines` — filters for guidelines, systematic reviews, and meta-analyses
- `search_recent_research` — limits results to a recent date range

## Setup

**1. Install dependencies**
```bash
pip install -r requirements.txt
```

**2. Add your API key to `.env`**
```
ANTHROPIC_API_KEY=sk-ant-...
```

**3. Run the app**
```bash
streamlit run app.py
```

## Project structure

```
PubMed-Agent-Proj/
├── app.py               # Streamlit UI (local alternative)
├── test.py              # Quick PubMed connectivity test
├── requirements.txt     # Python dependencies
├── Procfile             # Railway start command
├── .env                 # API key (never commit this)
├── agent/
│   ├── __init__.py
│   ├── pubmed_tools.py  # PubMed functions + tool definitions
│   └── research_agent.py
├── api/
│   ├── main.py          # FastAPI SSE endpoint (deployed on Railway)
│   └── requirements.txt
└── frontend/            # Next.js app (deployed on Vercel)
    └── app/
        ├── layout.tsx
        └── page.tsx
```

## Testing PubMed connectivity

To verify your Biopython/Entrez setup works before running the full agent:
```bash
python test.py
```

## Output format

The agent returns a structured report with:
- Executive Summary
- Key Findings (with PMIDs and URLs)
- Evidence-Based Recommendations
- Limitations & Gaps
- References
