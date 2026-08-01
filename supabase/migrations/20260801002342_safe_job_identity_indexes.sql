create unique index if not exists jobs_real_deduplication_key_unique_idx
  on public.jobs (deduplication_key)
  where deduplication_key is not null and not is_demo;

create unique index if not exists jobs_real_canonical_url_unique_idx
  on public.jobs (canonical_url)
  where canonical_url is not null and not is_demo;
