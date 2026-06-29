# Spotify Review Discovery Engine — Phase-wise Implementation Plan

## 0. Purpose

Build a standalone AI-powered review intelligence system for Spotify that:

- Ingests review/discussion data from App Store, Play Store, Reddit, and similar public sources
- Stores raw + processed data in a free-tier database
- Cleans, deduplicates, tags, segments, and summarizes review data
- Exposes the workflow through a public Streamlit app
- Produces insight-ready outputs for later product work

This system is independent from the Spotify Vibe MVP.

---

## 1. Target Outcome

Deliver a public Streamlit app with:

1. Source ingestion controls
2. Review explorer
3. Theme and segment dashboards
4. Insight summaries
5. Semantic query interface ("Ask the reviews")

The app should be deployable from GitHub via Streamlit Community Cloud.

---

## 2. Recommended Tech Stack

| Layer | Technology |
|---|---|
| **Frontend / App** | Streamlit |
| **Hosting** | Streamlit Community Cloud |
| **Database** | Supabase Postgres |
| **Vector Search** | pgvector on Supabase (same DB) |
| **Ingestion** | Python scripts |
| **Scheduling** | GitHub Actions (optional in later phase) |
| **Review Processing** | Python + pandas, scikit-learn for dedupe heuristics, optional LLM API for theme extraction / summarization |

### Why this stack
- Streamlit Community Cloud is free and designed for public data apps that deploy from GitHub.
- Supabase Free provides a Postgres database with 500 MB DB size and 1 GB file storage (free projects pause after one week of inactivity).
- `google-play-scraper` supports Python review crawling with pagination and review extraction without external dependencies.

---

## 3. Folder Structure

```text
spotify-review-engine/
├── app.py
├── requirements.txt
├── README.md
├── .env.example
├── .streamlit/
│   └── config.toml
├── sql/
│   ├── schema.sql
│   ├── seeds.sql
│   └── views.sql
├── src/
│   ├── config/
│   │   ├── settings.py
│   │   └── taxonomy.py
│   ├── db/
│   │   ├── supabase_client.py
│   │   ├── repository.py
│   │   └── migrations.py
│   ├── ingest/
│   │   ├── app_store_ingest.py
│   │   ├── play_store_ingest.py
│   │   ├── reddit_ingest.py
│   │   ├── manual_import.py
│   │   └── normalize.py
│   ├── process/
│   │   ├── clean_text.py
│   │   ├── dedupe.py
│   │   ├── language.py
│   │   ├── classify_themes.py
│   │   ├── segment_users.py
│   │   ├── aggregate_insights.py
│   │   └── evidence_builder.py
│   ├── rag/
│   │   ├── embed.py
│   │   ├── retrieve.py
│   │   └── answer.py
│   ├── ui/
│   │   ├── pages_overview.py
│   │   ├── pages_ingestion.py
│   │   ├── pages_explorer.py
│   │   ├── pages_insights.py
│   │   └── pages_ask.py
│   └── utils/
│       ├── logging.py
│       ├── hashing.py
│       ├── dates.py
│       └── validators.py
├── data/
│   ├── raw/
│   ├── processed/
│   └── manual_imports/
├── tests/
│   ├── test_cleaning.py
│   ├── test_dedupe.py
│   ├── test_taxonomy.py
│   └── test_ranking.py
└── .github/
    └── workflows/
        ├── ingest_playstore.yml
        ├── ingest_reddit.yml
        └── app_checks.yml
```

---

## 4. Database Schema (SQL)

### 4.1 `schema.sql`

```sql
create extension if not exists vector;

create table if not exists sources (
    id uuid primary key default gen_random_uuid(),
    source_name text not null,          -- app_store, play_store, reddit, manual_social
    source_type text not null,          -- review, discussion
    platform text not null,             -- Apple, GooglePlay, Reddit
    ingestion_method text not null,     -- api, scraper, csv_import
    created_at timestamptz default now()
);

create table if not exists raw_documents (
    id uuid primary key default gen_random_uuid(),
    source_id uuid references sources(id) on delete cascade,
    external_id text,
    title text,
    body text not null,
    author_name text,
    rating numeric,
    review_date timestamptz,
    country text,
    language text,
    url text,
    app_version text,
    metadata jsonb default '{}'::jsonb,
    ingested_at timestamptz default now(),
    raw_hash text not null
);

create unique index if not exists idx_raw_documents_source_external
on raw_documents(source_id, external_id);

create index if not exists idx_raw_documents_hash
on raw_documents(raw_hash);

create table if not exists clean_documents (
    id uuid primary key default gen_random_uuid(),
    raw_document_id uuid unique references raw_documents(id) on delete cascade,
    clean_text text not null,
    normalized_text text not null,
    detected_language text,
    is_duplicate boolean default false,
    duplicate_of uuid,
    token_count integer,
    processed_at timestamptz default now()
);

create table if not exists themes (
    id uuid primary key default gen_random_uuid(),
    theme_code text unique not null,
    theme_name text not null,
    theme_group text not null,
    theme_description text
);

create table if not exists document_themes (
    id uuid primary key default gen_random_uuid(),
    clean_document_id uuid references clean_documents(id) on delete cascade,
    theme_id uuid references themes(id) on delete cascade,
    confidence numeric not null,
    evidence_span text,
    extraction_method text not null,
    created_at timestamptz default now()
);

create table if not exists user_segments (
    id uuid primary key default gen_random_uuid(),
    segment_code text unique not null,
    segment_name text not null,
    segment_description text
);

create table if not exists document_segments (
    id uuid primary key default gen_random_uuid(),
    clean_document_id uuid references clean_documents(id) on delete cascade,
    segment_id uuid references user_segments(id) on delete cascade,
    confidence numeric not null,
    reasoning_summary text,
    created_at timestamptz default now()
);

create table if not exists insights (
    id uuid primary key default gen_random_uuid(),
    insight_title text not null,
    insight_summary text not null,
    insight_type text not null, -- friction, behavior, unmet_need, pattern
    supporting_doc_count integer not null default 0,
    theme_id uuid references themes(id),
    segment_id uuid references user_segments(id),
    created_at timestamptz default now()
);

create table if not exists embeddings (
    id uuid primary key default gen_random_uuid(),
    clean_document_id uuid unique references clean_documents(id) on delete cascade,
    embedding vector(1536),
    embedding_model text not null,
    created_at timestamptz default now()
);

create index if not exists idx_embeddings_vector
on embeddings using ivfflat (embedding vector_cosine_ops)
with (lists = 100);
```

---

## 5. Taxonomy Design

### 5.1 Theme Groups

#### Discovery Frictions
- `repetitive_recommendations`
- `same_artists_loop`
- `weak_novelty`
- `low_serendipity`
- `hard_to_find_new_music`
- `playlist_overdependence`
- `poor_explanation_of_recommendations`

#### Behavioral Intent
- `passive_discovery`
- `active_exploration`
- `mood_based_listening`
- `social_discovery`
- `genre_expansion`
- `niche_music_search`

#### Repetition Triggers
- `comfort_listening`
- `habit_loop`
- `low_trust_in_algo`
- `background_listening`
- `fear_of_bad_recommendations`

#### Unmet Needs
- `novelty_control`
- `explainability`
- `discovery_mode`
- `reset_recommendations`
- `friend_based_discovery`

### 5.2 User Segments

| Segment Code | Description |
|---|---|
| `passive_familiar_listener` | Listens passively to familiar music, low active discovery |
| `playlist_reliant_listener` | Relies heavily on curated playlists |
| `active_explorer` | Actively seeks out new music and genres |
| `mood_context_listener` | Selects music based on mood or activity context |
| `social_discovery_listener` | Discovers music via friends, social signals |

---

## 6. Data Ingestion Architecture

### Sources

| Source | Method | Library/Approach |
|---|---|---|
| Google Play Reviews | Scraper | `google-play-scraper` |
| App Store Reviews | RSS/Feed | Apple review RSS feed |
| Reddit Discussions | API/PRAW | `praw` or public JSON endpoints |
| Forums / Social | Manual CSV | CSV import pathway |

---

## 7. Source Modules

### `src/ingest/play_store_ingest.py`
- Fetch reviews for `com.spotify.music`
- Countries: `us`, `in`, `gb`; Sort: `newest`, `most_relevant`
- Normalize → write to `raw_documents`

### `src/ingest/app_store_ingest.py`
- Pull Apple review feed across storefronts/countries
- Normalize → write to `raw_documents`

### `src/ingest/reddit_ingest.py`
- Keywords: `spotify recommendations`, `spotify same songs`, `spotify discover weekly bad`, `spotify not discovering music`, `spotify repeats songs`
- Extract post title, body, comments → flatten → write to `raw_documents`

### `src/ingest/manual_import.py`
- Ingest CSV with fields: `source_name`, `external_id`, `title`, `body`, `author_name`, `rating`, `review_date`, `country`, `language`, `url`
- Validate format → insert to `raw_documents`

---

## 8. Data Normalization Contract

```json
{
    "source_name": "play_store",
    "source_type": "review",
    "platform": "GooglePlay",
    "ingestion_method": "scraper",
    "external_id": "...",
    "title": "...",
    "body": "...",
    "author_name": "...",
    "rating": 4,
    "review_date": "2026-06-01T00:00:00Z",
    "country": "us",
    "language": "en",
    "url": "...",
    "app_version": "...",
    "metadata": {}
}
```

**Rules:** `body` required · timestamps in ISO 8601 UTC · controlled `source_name` values · `raw_hash = sha256(normalized_text + source + external_id)`

---

## 9. Processing Pipeline

| Module | Responsibility |
|---|---|
| `clean_text.py` | Trim, strip HTML, normalize punctuation, remove boilerplate |
| `language.py` | Detect language, filter to English for MVP |
| `dedupe.py` | 3-stage: exact hash → TF-IDF cosine → semantic embedding |
| `classify_themes.py` | Rule-based pre-tagging + optional LLM refinement |
| `segment_users.py` | Infer primary user segment per review |
| `aggregate_insights.py` | Aggregate counts → generate PM-style insight summaries |

---

## 10. Embeddings + Semantic Query Layer

| Module | Responsibility |
|---|---|
| `embed.py` | Generate 1536-dim embeddings for `clean_text`, store in `embeddings` |
| `retrieve.py` | Top-k semantic search with source/theme/segment/rating/country filters |
| `answer.py` | Retrieve evidence → synthesize answer → return snippets |

---

## 11. Streamlit App Pages

| Page | Key Content |
|---|---|
| **Overview** | Totals, top themes, top segments, last ingestion time |
| **Ingestion** | Controls for all sources + normalization runner |
| **Review Explorer** | Filterable review table with themes, segments, evidence |
| **Themes & Segments** | Distribution charts, segment × theme matrix |
| **Insights** | Top 5 PM insight cards |
| **Ask the Reviews** | Free-text semantic Q&A with evidence snippets |

### UI Theme
- Dark sidebar · white/neutral content cards · `#1DB954` Spotify green accents only for key highlights

---

## 12. Phase-wise Delivery Plan

### ✅ Phase 1 — Repository + Database Setup
**Deliverables:** repo initialized, `requirements.txt`, Supabase schema applied, taxonomy file, DB connection test

**Exit Criteria:** local app can connect to Supabase, tables exist, repo runs without syntax errors

### Phase 2 — Ingestion Connectors
**Exit Criteria:** ≥100 documents per source insertable, no duplicate collision errors

### Phase 3 — Cleaning + Deduplication
**Exit Criteria:** raw → clean documents pipeline works, duplicates flagged consistently

### Phase 4 — Theme Extraction + User Segmentation
**Exit Criteria:** every processed review has ≥0 themes, one primary segment or "unknown"

### Phase 5 — Insight Aggregation
**Exit Criteria:** insights page loads meaningful summary cards backed by evidence

### Phase 6 — Embeddings + Semantic Search
**Exit Criteria:** user can ask a question and get evidence-backed answer snippets

### Phase 7 — Streamlit UI + Deployment
**Exit Criteria:** app publicly reachable, demonstrates full ingestion → processing → query workflow

---

## 13. `requirements.txt`

```
streamlit
pandas
numpy
supabase
psycopg2-binary
sqlalchemy
google-play-scraper
requests
beautifulsoup4
scikit-learn
python-dotenv
pydantic
plotly
tqdm
langdetect
sentence-transformers
# Optional LLM:
# openai
# anthropic
```

---

## 14. Environment Variables

```
SUPABASE_URL=
SUPABASE_KEY=
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
REDDIT_CLIENT_ID=
REDDIT_CLIENT_SECRET=
REDDIT_USER_AGENT=
```

---

## 15. MVP Acceptance Criteria

- [ ] Reviews from ≥3 sources ingested
- [ ] All records normalized into one DB schema
- [ ] Duplicates handled
- [ ] Themes assigned
- [ ] User segments inferred
- [ ] Insights generated
- [ ] Streamlit app exposes end-to-end workflow
- [ ] App publicly accessible via link

---

## 16. Non-Goals

Do **not** implement: private user research ingestion · recommendation generation · Spotify account integration · production-grade large-scale scraping infrastructure.

---

## 17. Critical Path

> `ingestion → storage → cleaning → themes → segments → insights → public app`
>
> Do not over-engineer the LLM layer first.
