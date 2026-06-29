-- ============================================================
-- views.sql — Convenience views for Streamlit dashboards
-- Run AFTER schema.sql and seeds.sql
-- ============================================================

-- Overview: total counts per source
create or replace view v_source_counts as
select
    s.source_name,
    s.platform,
    count(r.id) as total_raw,
    count(c.id) as total_clean,
    count(c.id) filter (where c.is_duplicate = true) as duplicates,
    max(r.ingested_at) as last_ingested_at
from sources s
left join raw_documents r on r.source_id = s.id
left join clean_documents c on c.raw_document_id = r.id
group by s.source_name, s.platform;

-- Theme distribution: count of reviews per theme
create or replace view v_theme_distribution as
select
    t.theme_code,
    t.theme_name,
    t.theme_group,
    count(dt.id) as doc_count,
    avg(dt.confidence) as avg_confidence
from themes t
left join document_themes dt on dt.theme_id = t.id
group by t.id, t.theme_code, t.theme_name, t.theme_group
order by doc_count desc;

-- Segment distribution: count of reviews per segment
create or replace view v_segment_distribution as
select
    us.segment_code,
    us.segment_name,
    count(ds.id) as doc_count,
    avg(ds.confidence) as avg_confidence
from user_segments us
left join document_segments ds on ds.segment_id = us.id
group by us.id, us.segment_code, us.segment_name
order by doc_count desc;

-- Segment x Theme matrix: for heatmap in Streamlit
create or replace view v_segment_theme_matrix as
select
    us.segment_code,
    us.segment_name,
    t.theme_code,
    t.theme_name,
    t.theme_group,
    count(dt.id) as doc_count
from user_segments us
cross join themes t
left join document_segments ds on ds.segment_id = us.id
left join document_themes dt on dt.clean_document_id = ds.clean_document_id and dt.theme_id = t.id
group by us.segment_code, us.segment_name, t.theme_code, t.theme_name, t.theme_group
order by us.segment_code, doc_count desc;

-- Review explorer: full joined view for the Review Explorer page
create or replace view v_review_explorer as
select
    r.id as raw_id,
    c.id as clean_id,
    s.source_name,
    s.platform,
    r.author_name,
    r.rating,
    r.review_date,
    r.country,
    r.language,
    r.app_version,
    r.url,
    r.body as raw_text,
    c.clean_text,
    c.detected_language,
    c.is_duplicate,
    c.token_count,
    r.ingested_at,
    c.processed_at
from raw_documents r
join sources s on s.id = r.source_id
left join clean_documents c on c.raw_document_id = r.id;
