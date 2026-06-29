-- 3. Create Hybrid Search RPC function
-- Combines pure vector semantic search with Postgres Full-Text Keyword Search
create or replace function hybrid_search (
  query_text text,
  query_embedding vector(384),
  match_count int
)
returns table (
  id uuid,
  clean_document_id uuid,
  clean_text text,
  similarity float
)
language sql stable
as $$
  select
    e.id,
    e.clean_document_id,
    cd.clean_text,
    -- Compute base semantic similarity (usually between 0.0 and 1.0)
    (1 - (e.embedding <=> query_embedding)) + 
    -- ADD a massive 1.0 boost if the document contains the exact keywords
    (case when to_tsvector('english', cd.clean_text) @@ websearch_to_tsquery('english', query_text) then 1.0 else 0.0 end) as similarity
  from embeddings e
  join clean_documents cd on e.clean_document_id = cd.id
  order by similarity desc
  limit match_count;
$$;
