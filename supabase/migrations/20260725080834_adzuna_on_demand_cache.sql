-- Adzuna is licensed/on-demand and must not be scheduled automatically.
update public.job_sources
set
  enabled = false,
  status = 'waiting_for_key',
  sync_mode = 'on_demand',
  sync_interval_minutes = null,
  max_results_per_request = 20,
  requires_api_key = true,
  public_notes = 'Menunggu pengujian kredensial Adzuna pada server.'
where slug = 'adzuna'
  and status <> 'active';

-- One cache entry per source/query. Remove any historical duplicate rows
-- before enforcing uniqueness.
delete from public.job_source_payloads older
using public.job_source_payloads newer
where older.source_id = newer.source_id
  and older.external_id = newer.external_id
  and older.external_id is not null
  and (
    older.fetched_at < newer.fetched_at
    or (older.fetched_at = newer.fetched_at and older.id < newer.id)
  );

create unique index if not exists job_source_payloads_source_external_unique_idx
  on public.job_source_payloads (source_id, external_id);

-- Explicitly prevent Adzuna from being run by the cron registry.
update public.job_cron_config
set
  enabled = false,
  status = 'disabled',
  last_error = null
where source_slug = 'adzuna';

