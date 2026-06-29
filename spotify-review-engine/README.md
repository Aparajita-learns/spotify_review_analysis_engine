# Spotify Review Discovery Engine

An AI-powered review intelligence system that ingests, processes, and analyzes user feedback from App Store, Play Store, Reddit, and social platforms to surface product insights about Spotify's music discovery experience.

---

## Architecture

```
ingestion → storage → cleaning → themes → segments → insights → public Streamlit app
```

**Stack:** Python · Streamlit · Supabase Postgres · pgvector · scikit-learn · (optional) OpenAI/Anthropic

---

## Quick Start

### 1. Clone and install

```bash
git clone https://github.com/YOUR_USERNAME/spotify-review-engine.git
cd spotify-review-engine
pip install -r requirements.txt
```

### 2. Set up environment

```bash
cp .env.example .env
# Fill in SUPABASE_URL and SUPABASE_KEY
```

### 3. Initialize the database

Run the following SQL files in your **Supabase SQL Editor** in order:

1. `sql/schema.sql` — creates all tables and indexes
2. `sql/seeds.sql` — seeds themes and user segments taxonomy
3. `sql/views.sql` — creates convenience views for dashboards

### 4. Run smoke tests

```bash
python tests/test_db_connection.py
```

All 6 checks should pass.

### 5. Launch the app

```bash
streamlit run app.py
```

---

## Project Structure

```
spotify-review-engine/
├── app.py                      # Streamlit entry point
├── requirements.txt
├── sql/                        # Database SQL files
│   ├── schema.sql
│   ├── seeds.sql
│   └── views.sql
├── src/
│   ├── config/                 # Settings and taxonomy
│   ├── db/                     # Supabase client and repository
│   ├── ingest/                 # Data ingestion connectors (Phase 2)
│   ├── process/                # Text processing pipeline (Phase 3-5)
│   ├── rag/                    # Embeddings and semantic search (Phase 6)
│   ├── ui/                     # Streamlit page modules
│   └── utils/                  # Shared utilities
├── data/                       # Local raw/processed/manual data
└── tests/                      # Test suite
```

---

## Delivery Phases

| Phase | Status | Description |
|---|---|---|
| 1 — Repo + DB Setup | ✅ Complete | Schema, taxonomy, client, smoke test |
| 2 — Ingestion | 🔜 Next | Play Store, App Store, Reddit, CSV |
| 3 — Cleaning + Dedupe | ⏳ Planned | Text cleaning, language detect, dedup |
| 4 — Theme + Segment | ⏳ Planned | Rule-based + LLM classification |
| 5 — Insights | ⏳ Planned | PM-ready insight aggregation |
| 6 — Semantic Search | ⏳ Planned | Embeddings + Ask the Reviews |
| 7 — Deployment | ⏳ Planned | Streamlit Community Cloud |

---

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `SUPABASE_URL` | ✅ | Your Supabase project URL |
| `SUPABASE_KEY` | ✅ | Supabase anon or service role key |
| `OPENAI_API_KEY` | Optional | For LLM theme extraction (Phase 4+) |
| `ANTHROPIC_API_KEY` | Optional | Alternative LLM provider |
| `REDDIT_CLIENT_ID` | Optional | Reddit OAuth app credentials |
| `REDDIT_CLIENT_SECRET` | Optional | Reddit OAuth app credentials |
| `REDDIT_USER_AGENT` | Optional | Defaults to `spotify-review-engine/0.1` |

---

## Deployment

Deploy to **Streamlit Community Cloud**:

1. Push repo to GitHub
2. Connect to [share.streamlit.io](https://share.streamlit.io)
3. Set entry point: `app.py`
4. Add `SUPABASE_URL` and `SUPABASE_KEY` in Streamlit Secrets

> ⚠️ Free Supabase projects pause after 1 week of inactivity. Open the app before any demo or submission.

---

## Non-Goals

This is a **review analysis workflow tool**, not an end-user product. It does not:
- Generate music recommendations for end users
- Integrate with actual Spotify accounts
- Handle private user research data
