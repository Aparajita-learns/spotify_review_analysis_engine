-- ============================================================
-- Spotify Review Discovery Engine — Database Schema
-- Run this in your Supabase SQL Editor to initialize all tables
-- ============================================================

-- Enable the pgvector extension for semantic search (Phase 6)
create extension if not exists vector;

-- ============================================================
-- SOURCES — registry of ingestion sources
-- ============================================================
create table if not exists sources (
    id              uuid primary key default gen_random_uuid(),
    source_name     text not null,          -- app_store | play_store | reddit | manual_social
    source_type     text not null,          -- review | discussion
    platform        text not null,          -- Apple | GooglePlay | Reddit | Manual
    ingestion_method text not null,         -- api | scraper | csv_import
    created_at      timestamptz default now()
);

-- ============================================================
-- RAW_DOCUMENTS — unmodified ingested records
-- ============================================================
create table if not exists raw_documents (
    id              uuid primary key default gen_random_uuid(),
    source_id       uuid references sources(id) on delete cascade,
    external_id     text,                   -- original review ID from source platform
    title           text,
    body            text not null,
    author_name     text,
    rating          numeric,                -- 1-5 stars where applicable
    review_date     timestamptz,
    country         text,
    language        text,
    url             text,
    app_version     text,
    metadata        jsonb default '{}'::jsonb,
    ingested_at     timestamptz default now(),
    raw_hash        text not null           -- sha256 for deduplication
);

-- Unique constraint: one (source, external_id) pair only
create unique index if not exists idx_raw_documents_source_external
    on raw_documents(source_id, external_id)
    where external_id is not null;

-- Fast lookup by hash for exact-duplicate detection
create index if not exists idx_raw_documents_hash
    on raw_documents(raw_hash);

-- ============================================================
-- CLEAN_DOCUMENTS — processed, deduplicated records
-- ============================================================
create table if not exists clean_documents (
    id              uuid primary key default gen_random_uuid(),
    raw_document_id uuid unique references raw_documents(id) on delete cascade,
    clean_text      text not null,
    normalized_text text not null,          -- lowercase, stripped, for dedupe
    detected_language text,
    is_duplicate    boolean default false,
    duplicate_of    uuid,                   -- FK to another clean_document if duplicate
    token_count     integer,
    processed_at    timestamptz default now()
);

-- ============================================================
-- THEMES — taxonomy of discovery-related themes
-- ============================================================
create table if not exists themes (
    id              uuid primary key default gen_random_uuid(),
    theme_code      text unique not null,   -- e.g. repetitive_recommendations
    theme_name      text not null,
    theme_group     text not null,          -- discovery_frictions | behavioral_intent | repetition_triggers | unmet_needs
    theme_description text
);

-- ============================================================
-- DOCUMENT_THEMES — many-to-many: reviews <-> themes
-- ============================================================
create table if not exists document_themes (
    id                  uuid primary key default gen_random_uuid(),
    clean_document_id   uuid references clean_documents(id) on delete cascade,
    theme_id            uuid references themes(id) on delete cascade,
    confidence          numeric not null check (confidence between 0 and 1),
    evidence_span       text,               -- quoted text that triggered this theme
    extraction_method   text not null,      -- rules | llm | hybrid
    created_at          timestamptz default now()
);

-- ============================================================
-- USER_SEGMENTS — taxonomy of user behavioral segments
-- ============================================================
create table if not exists user_segments (
    id              uuid primary key default gen_random_uuid(),
    segment_code    text unique not null,   -- e.g. passive_familiar_listener
    segment_name    text not null,
    segment_description text
);

-- ============================================================
-- DOCUMENT_SEGMENTS — one primary segment per review
-- ============================================================
create table if not exists document_segments (
    id                  uuid primary key default gen_random_uuid(),
    clean_document_id   uuid references clean_documents(id) on delete cascade,
    segment_id          uuid references user_segments(id) on delete cascade,
    confidence          numeric not null check (confidence between 0 and 1),
    reasoning_summary   text,
    created_at          timestamptz default now()
);

-- ============================================================
-- INSIGHTS — aggregated PM-ready insight cards
-- ============================================================
create table if not exists insights (
    id                  uuid primary key default gen_random_uuid(),
    insight_title       text not null,
    insight_summary     text not null,
    insight_type        text not null,      -- friction | behavior | unmet_need | pattern
    supporting_doc_count integer not null default 0,
    theme_id            uuid references themes(id),
    segment_id          uuid references user_segments(id),
    created_at          timestamptz default now()
);

-- ============================================================
-- EMBEDDINGS — vector embeddings for semantic search (Phase 6)
-- ============================================================
create table if not exists embeddings (
    id                  uuid primary key default gen_random_uuid(),
    clean_document_id   uuid unique references clean_documents(id) on delete cascade,
    embedding           vector(1536),       -- OpenAI text-embedding-3-small or similar
    embedding_model     text not null,
    created_at          timestamptz default now()
);

-- IVFFlat index for approximate nearest-neighbor search
create index if not exists idx_embeddings_vector
    on embeddings using ivfflat (embedding vector_cosine_ops)
    with (lists = 100);
