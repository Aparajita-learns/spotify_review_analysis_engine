-- 1. Drop existing table and recreate it with 384 dimensions
drop table if exists embeddings cascade;

create table embeddings (
    id                  uuid primary key default gen_random_uuid(),
    clean_document_id   uuid unique references clean_documents(id) on delete cascade,
    embedding           vector(384),       -- Changed from 1536 to 384 for sentence-transformers
    embedding_model     text not null,
    created_at          timestamptz default now()
);

-- Recreate index
create index if not exists idx_embeddings_vector
    on embeddings using ivfflat (embedding vector_cosine_ops)
    with (lists = 100);

-- 2. Create RPC function for semantic search
create or replace function match_documents (
  query_embedding vector(384),
  match_threshold float,
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
    1 - (e.embedding <=> query_embedding) as similarity
  from embeddings e
  join clean_documents cd on e.clean_document_id = cd.id
  where 1 - (e.embedding <=> query_embedding) > match_threshold
  order by e.embedding <=> query_embedding
  limit match_count;
$$;
