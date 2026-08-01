alter table public.jobs
  add column if not exists channel_posted_at timestamp with time zone;

create index if not exists jobs_channel_pending_idx
  on public.jobs (published_at desc)
  where is_active
    and not is_demo
    and channel_posted_at is null;
