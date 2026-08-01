-- Premium, compliance-first multi-source job aggregator for MrKarir AI.
-- This migration is additive: existing product tables and demo jobs are preserved.

create extension if not exists pgcrypto;

create table if not exists public.companies (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  normalized_name text not null,
  logo_url text,
  website_url text,
  careers_url text,
  industry text,
  headquarters text,
  description text,
  verification_status text not null default 'unverified'
    check (verification_status in ('unverified','needs_review','verified','rejected')),
  verified_at timestamptz,
  verified_by uuid references auth.users(id) on delete set null,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create unique index if not exists companies_normalized_name_unique_idx
  on public.companies (normalized_name);

create table if not exists public.job_sources (
  id uuid primary key default gen_random_uuid(),
  slug text not null unique,
  display_name text not null,
  provider_type text not null
    check (provider_type in ('direct_api','licensed_api','ats','admin')),
  base_url text not null,
  attribution_name text not null,
  attribution_url text not null,
  terms_url text,
  api_documentation_url text,
  enabled boolean not null default false,
  status text not null default 'disabled'
    check (status in ('active','waiting_for_key','waiting_for_license','rate_limited','degraded','disabled','failed')),
  sync_mode text not null default 'scheduled'
    check (sync_mode in ('scheduled','on_demand','hybrid','disabled')),
  sync_interval_minutes integer check (sync_interval_minutes is null or sync_interval_minutes >= 15),
  license_notes text,
  compliance_notes text,
  last_tested_at timestamptz,
  last_success_at timestamptz,
  last_failure_at timestamptz,
  last_error_code text,
  last_error_message text,
  request_timeout_ms integer not null default 8000 check (request_timeout_ms between 1000 and 30000),
  max_results_per_request integer not null default 20 check (max_results_per_request between 1 and 100),
  supports_pagination boolean not null default true,
  supports_remote_filter boolean not null default false,
  requires_api_key boolean not null default false,
  requires_license boolean not null default false,
  public_notes text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.company_job_boards (
  id uuid primary key default gen_random_uuid(),
  company_id uuid references public.companies(id) on delete cascade,
  source_id uuid not null references public.job_sources(id) on delete restrict,
  board_identifier text not null,
  api_region text not null default 'global' check (api_region in ('global','eu')),
  official_careers_url text not null,
  verification_status text not null default 'needs_review'
    check (verification_status in ('needs_review','verified','rejected','disabled')),
  verified_at timestamptz,
  verified_by uuid references auth.users(id) on delete set null,
  is_enabled boolean not null default false,
  last_synced_at timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (source_id, board_identifier)
);

alter table public.jobs
  add column if not exists source_id uuid references public.job_sources(id) on delete set null,
  add column if not exists source_job_url text,
  add column if not exists canonical_url text,
  add column if not exists normalized_title text,
  add column if not exists company_id uuid references public.companies(id) on delete set null,
  add column if not exists company_name_raw text,
  add column if not exists location_text text,
  add column if not exists country_code text,
  add column if not exists is_remote boolean not null default false,
  add column if not exists remote_scope text,
  add column if not exists timezone_restrictions text[] not null default '{}',
  add column if not exists salary_is_estimated boolean not null default false,
  add column if not exists salary_source text,
  add column if not exists description_html text,
  add column if not exists description_text text,
  add column if not exists summary text,
  add column if not exists language text,
  add column if not exists source_updated_at timestamptz,
  add column if not exists first_seen_at timestamptz not null default now(),
  add column if not exists last_seen_at timestamptz not null default now(),
  add column if not exists last_checked_at timestamptz,
  add column if not exists verification_status text not null default 'imported',
  add column if not exists fraud_risk_level text not null default 'unknown',
  add column if not exists fraud_flags text[] not null default '{}',
  add column if not exists content_hash text,
  add column if not exists deduplication_key text,
  add column if not exists is_remote_eligible_indonesia boolean,
  add column if not exists easy_apply boolean not null default false;

update public.jobs
set
  source_job_url = coalesce(source_job_url, source_url),
  canonical_url = coalesce(canonical_url, source_url),
  normalized_title = coalesce(normalized_title, lower(regexp_replace(trim(title), '\s+', ' ', 'g'))),
  company_name_raw = coalesce(company_name_raw, company_name),
  location_text = coalesce(location_text, location),
  is_remote = coalesce(work_system = 'remote', false),
  description_text = coalesce(description_text, description),
  verification_status = case
    when is_active then 'published'
    else 'archived'
  end,
  content_hash = coalesce(
    content_hash,
    encode(digest(coalesce(title,'') || '|' || coalesce(company_name,'') || '|' || coalesce(location,'') || '|' || coalesce(description,''), 'sha256'), 'hex')
  ),
  deduplication_key = coalesce(
    deduplication_key,
    lower(regexp_replace(coalesce(company_name,'') || '|' || coalesce(title,'') || '|' || coalesce(location,''), '[^a-zA-Z0-9]+', '', 'g'))
  )
where source_job_url is null
   or canonical_url is null
   or normalized_title is null
   or company_name_raw is null
   or description_text is null
   or content_hash is null
   or deduplication_key is null;

do $$
begin
  if not exists (
    select 1 from pg_constraint
    where conrelid = 'public.jobs'::regclass
      and conname = 'jobs_verification_status_check'
  ) then
    alter table public.jobs add constraint jobs_verification_status_check
      check (verification_status in ('imported','needs_review','verified_source','published','expired','suspended','rejected','archived'));
  end if;
  if not exists (
    select 1 from pg_constraint
    where conrelid = 'public.jobs'::regclass
      and conname = 'jobs_fraud_risk_level_check'
  ) then
    alter table public.jobs add constraint jobs_fraud_risk_level_check
      check (fraud_risk_level in ('unknown','low','medium','high'));
  end if;
end
$$;

create table if not exists public.job_source_payloads (
  id uuid primary key default gen_random_uuid(),
  source_id uuid not null references public.job_sources(id) on delete cascade,
  job_id uuid references public.jobs(id) on delete cascade,
  external_id text,
  payload jsonb not null,
  payload_hash text,
  fetched_at timestamptz not null default now(),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.job_sync_runs (
  id uuid primary key default gen_random_uuid(),
  source_id uuid not null references public.job_sources(id) on delete cascade,
  request_id uuid not null default gen_random_uuid(),
  trigger_type text not null default 'scheduled'
    check (trigger_type in ('scheduled','manual','on_demand','retry')),
  status text not null default 'running'
    check (status in ('running','succeeded','partial','failed','skipped_locked')),
  started_at timestamptz not null default now(),
  finished_at timestamptz,
  received_count integer not null default 0,
  inserted_count integer not null default 0,
  updated_count integer not null default 0,
  skipped_count integer not null default 0,
  rejected_count integer not null default 0,
  error_code text,
  error_message text,
  log_context jsonb not null default '{}',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create unique index if not exists job_sync_runs_source_running_unique_idx
  on public.job_sync_runs (source_id)
  where status = 'running';

create table if not exists public.job_validation_results (
  id uuid primary key default gen_random_uuid(),
  job_id uuid not null references public.jobs(id) on delete cascade,
  validator text not null,
  status text not null check (status in ('passed','warning','failed','not_run')),
  risk_level text not null default 'unknown' check (risk_level in ('unknown','low','medium','high')),
  flags text[] not null default '{}',
  details jsonb not null default '{}',
  checked_at timestamptz not null default now(),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.saved_searches (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  name text not null,
  filters jsonb not null default '{}',
  alert_enabled boolean not null default false,
  alert_frequency text not null default 'daily'
    check (alert_frequency in ('instant','daily','weekly','disabled')),
  last_alerted_at timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.job_alert_deliveries (
  id uuid primary key default gen_random_uuid(),
  saved_search_id uuid not null references public.saved_searches(id) on delete cascade,
  user_id uuid not null references auth.users(id) on delete cascade,
  channel text not null default 'in_app' check (channel in ('in_app','email')),
  status text not null default 'queued' check (status in ('queued','sent','failed','skipped')),
  job_ids uuid[] not null default '{}',
  provider_message_id text,
  error_message text,
  sent_at timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.job_reports (
  id uuid primary key default gen_random_uuid(),
  job_id uuid references public.jobs(id) on delete set null,
  user_id uuid references auth.users(id) on delete set null,
  reason text not null check (reason in ('expired','broken_link','suspected_scam','duplicate','incorrect_information','other')),
  details text,
  status text not null default 'open' check (status in ('open','reviewing','resolved','dismissed')),
  reviewed_by uuid references auth.users(id) on delete set null,
  reviewed_at timestamptz,
  resolution_notes text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.applications (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  job_id uuid references public.jobs(id) on delete set null,
  position text not null,
  company text not null,
  location text,
  source_url text,
  salary text,
  status text not null default 'saved'
    check (status in ('saved','planning','applied','test','interview','waiting','accepted','rejected','canceled')),
  applied_at date,
  test_at timestamptz,
  interview_at timestamptz,
  recruiter_contact text,
  notes text,
  resume_id uuid references public.resumes(id) on delete set null,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

insert into public.applications (
  id, user_id, position, company, location, source_url, salary, status,
  applied_at, test_at, interview_at, recruiter_contact, notes, created_at, updated_at
)
select
  id, user_id, position, company, location, source_url, salary, status,
  applied_at, test_at, interview_at, recruiter_contact, notes, created_at, updated_at
from public.job_applications
on conflict (id) do nothing;

create unique index if not exists saved_jobs_user_job_unique_idx
  on public.saved_jobs (user_id, job_id)
  where job_id is not null;
create index if not exists companies_verification_idx on public.companies (verification_status);
create index if not exists company_job_boards_source_idx on public.company_job_boards (source_id, verification_status, is_enabled);
create index if not exists jobs_source_id_external_idx on public.jobs (source_id, external_id);
create index if not exists jobs_canonical_url_idx on public.jobs (canonical_url) where canonical_url is not null;
create index if not exists jobs_deduplication_key_idx on public.jobs (deduplication_key) where deduplication_key is not null;
create index if not exists jobs_public_feed_idx on public.jobs (published_at desc)
  where is_active and verification_status = 'published' and fraud_risk_level <> 'high';
create index if not exists jobs_country_remote_idx on public.jobs (country_code, is_remote, published_at desc);
create index if not exists jobs_salary_filter_idx on public.jobs (salary_currency, salary_min, salary_max)
  where salary_min is not null or salary_max is not null;
create index if not exists job_source_payloads_job_idx on public.job_source_payloads (job_id, fetched_at desc);
create index if not exists job_source_payloads_payload_gin_idx on public.job_source_payloads using gin (payload jsonb_path_ops);
create index if not exists job_sync_runs_source_started_idx on public.job_sync_runs (source_id, started_at desc);
create index if not exists job_validation_results_job_idx on public.job_validation_results (job_id, checked_at desc);
create index if not exists saved_searches_user_idx on public.saved_searches (user_id, updated_at desc);
create index if not exists job_alert_deliveries_user_idx on public.job_alert_deliveries (user_id, created_at desc);
create index if not exists job_reports_status_idx on public.job_reports (status, created_at desc);
create index if not exists applications_user_status_idx on public.applications (user_id, status, updated_at desc);

insert into public.job_sources (
  slug, display_name, provider_type, base_url, attribution_name, attribution_url,
  terms_url, api_documentation_url, enabled, status, sync_mode,
  sync_interval_minutes, compliance_notes, max_results_per_request,
  supports_pagination, supports_remote_filter, requires_api_key, requires_license,
  public_notes
) values
  ('jooble','Jooble','licensed_api','https://jooble.org/api','Jooble','https://jooble.org',
   'https://jooble.org/info/terms','https://help.jooble.org/en/support/solutions/articles/60001448238-rest-api-documentation',
   false,'waiting_for_key','on_demand',null,'POST only from backend; never expose the API key.',20,true,true,true,false,
   'Menunggu JOOBLE_API_KEY pada server.'),
  ('himalayas','Himalayas','direct_api','https://himalayas.app/jobs/api','Himalayas','https://himalayas.app/jobs',
   'https://himalayas.app/terms','https://himalayas.app/jobs/api',
   true,'active','hybrid',60,'Use the official public jobs API and preserve attribution.',20,true,true,false,false,
   'Sumber remote resmi; maksimal 20 hasil per permintaan.'),
  ('remotive','Remotive','direct_api','https://remotive.com/api/remote-jobs','Remotive','https://remotive.com/remote-jobs',
   'https://remotive.com/terms-of-use','https://github.com/remotive-com/remote-jobs-api',
   true,'active','scheduled',360,'Attribution is required. Do not republish these jobs to third-party aggregators or Google Jobs.',20,false,true,false,false,
   'Lowongan remote dengan atribusi Remotive.'),
  ('arbeitnow','Arbeitnow','direct_api','https://www.arbeitnow.com/api/job-board-api','Arbeitnow','https://www.arbeitnow.com',
   'https://www.arbeitnow.com/terms-and-conditions','https://www.arbeitnow.com/blog/job-board-api',
   true,'active','hybrid',120,'Use the public job-board API, preserve source URL, and respect pagination.',20,true,true,false,false,
   'Sumber Eropa, remote, dan visa sponsorship.'),
  ('greenhouse','Greenhouse Job Board API','ats','https://boards-api.greenhouse.io/v1/boards','Greenhouse','https://www.greenhouse.com',
   'https://www.greenhouse.com/legal','https://developers.greenhouse.io/job-board.html',
   false,'disabled','scheduled',180,'Only admin-verified board tokens from official company career pages. GET only; applications remain external.',100,false,false,false,false,
   'Aktif setelah admin menambahkan board token resmi yang telah diverifikasi.'),
  ('lever','Lever Postings API','ats','https://api.lever.co/v0/postings','Lever','https://www.lever.co',
   'https://www.lever.co/terms-of-use','https://github.com/lever/postings-api',
   false,'disabled','scheduled',180,'Only admin-verified site identifiers. Handle 429 with backoff; applications remain external.',100,true,false,false,false,
   'Aktif setelah admin menambahkan site identifier resmi yang telah diverifikasi.'),
  ('adzuna','Adzuna','licensed_api','https://api.adzuna.com/v1/api/jobs','Adzuna','https://www.adzuna.com',
   'https://www.adzuna.com/terms-and-conditions','https://developer.adzuna.com',
   false,'waiting_for_license','disabled',null,'Connector is prepared but disabled until API credentials and redistribution rights are confirmed.',20,true,true,true,true,
   'Menunggu kredensial dan konfirmasi lisensi.')
on conflict (slug) do update set
  display_name = excluded.display_name,
  provider_type = excluded.provider_type,
  base_url = excluded.base_url,
  attribution_name = excluded.attribution_name,
  attribution_url = excluded.attribution_url,
  terms_url = excluded.terms_url,
  api_documentation_url = excluded.api_documentation_url,
  sync_interval_minutes = excluded.sync_interval_minutes,
  compliance_notes = excluded.compliance_notes,
  max_results_per_request = excluded.max_results_per_request,
  supports_pagination = excluded.supports_pagination,
  supports_remote_filter = excluded.supports_remote_filter,
  requires_api_key = excluded.requires_api_key,
  requires_license = excluded.requires_license,
  public_notes = excluded.public_notes,
  updated_at = now();

update public.jobs j
set source_id = s.id
from public.job_sources s
where j.source_id is null and lower(j.source) = lower(s.display_name);

alter table public.companies enable row level security;
alter table public.job_sources enable row level security;
alter table public.company_job_boards enable row level security;
alter table public.job_source_payloads enable row level security;
alter table public.job_sync_runs enable row level security;
alter table public.job_validation_results enable row level security;
alter table public.saved_searches enable row level security;
alter table public.job_alert_deliveries enable row level security;
alter table public.job_reports enable row level security;
alter table public.applications enable row level security;

grant select on public.companies, public.job_sources to anon, authenticated;
grant select on public.company_job_boards to authenticated;
grant insert, update, delete on public.companies, public.job_sources, public.company_job_boards to authenticated;
grant select, insert, update, delete on public.job_source_payloads, public.job_sync_runs, public.job_validation_results to authenticated;
grant select, insert, update, delete on public.saved_searches, public.job_alert_deliveries, public.job_reports, public.applications to authenticated;

drop policy if exists "jobs_public_or_admin_read" on public.jobs;
create policy "jobs_public_or_admin_read"
on public.jobs for select
to anon, authenticated
using (
  (
    is_active
    and verification_status = 'published'
    and fraud_risk_level <> 'high'
    and (expires_at is null or expires_at >= now())
  )
  or coalesce((select auth.jwt()) -> 'app_metadata' ->> 'role', '') in ('admin','super_admin','moderator')
);

create policy "companies_public_read" on public.companies for select to anon, authenticated using (true);
create policy "companies_admin_write" on public.companies for all to authenticated
  using (coalesce((select auth.jwt()) -> 'app_metadata' ->> 'role','') in ('admin','super_admin'))
  with check (coalesce((select auth.jwt()) -> 'app_metadata' ->> 'role','') in ('admin','super_admin'));

create policy "job_sources_public_read" on public.job_sources for select to anon, authenticated using (true);
create policy "job_sources_admin_write" on public.job_sources for all to authenticated
  using (coalesce((select auth.jwt()) -> 'app_metadata' ->> 'role','') in ('admin','super_admin'))
  with check (coalesce((select auth.jwt()) -> 'app_metadata' ->> 'role','') in ('admin','super_admin'));

create policy "company_boards_admin_all" on public.company_job_boards for all to authenticated
  using (coalesce((select auth.jwt()) -> 'app_metadata' ->> 'role','') in ('admin','super_admin'))
  with check (coalesce((select auth.jwt()) -> 'app_metadata' ->> 'role','') in ('admin','super_admin'));

create policy "job_payloads_admin_read" on public.job_source_payloads for select to authenticated
  using (coalesce((select auth.jwt()) -> 'app_metadata' ->> 'role','') in ('admin','super_admin','moderator'));
create policy "sync_runs_admin_read" on public.job_sync_runs for select to authenticated
  using (coalesce((select auth.jwt()) -> 'app_metadata' ->> 'role','') in ('admin','super_admin','moderator'));
create policy "validation_admin_read" on public.job_validation_results for select to authenticated
  using (coalesce((select auth.jwt()) -> 'app_metadata' ->> 'role','') in ('admin','super_admin','moderator'));

create policy "saved_searches_owner_all" on public.saved_searches for all to authenticated
  using ((select auth.uid()) = user_id) with check ((select auth.uid()) = user_id);
create policy "alert_deliveries_owner_read" on public.job_alert_deliveries for select to authenticated
  using ((select auth.uid()) = user_id);

create policy "job_reports_owner_insert" on public.job_reports for insert to authenticated
  with check ((select auth.uid()) = user_id);
create policy "job_reports_owner_or_admin_read" on public.job_reports for select to authenticated
  using ((select auth.uid()) = user_id or coalesce((select auth.jwt()) -> 'app_metadata' ->> 'role','') in ('admin','super_admin','moderator'));
create policy "job_reports_admin_update" on public.job_reports for update to authenticated
  using (coalesce((select auth.jwt()) -> 'app_metadata' ->> 'role','') in ('admin','super_admin','moderator'))
  with check (coalesce((select auth.jwt()) -> 'app_metadata' ->> 'role','') in ('admin','super_admin','moderator'));

create policy "applications_owner_all" on public.applications for all to authenticated
  using ((select auth.uid()) = user_id) with check ((select auth.uid()) = user_id);

do $$
declare
  target_table text;
begin
  foreach target_table in array array[
    'companies','job_sources','company_job_boards','job_source_payloads',
    'job_sync_runs','job_validation_results','saved_searches',
    'job_alert_deliveries','job_reports','applications'
  ]
  loop
    execute format('drop trigger if exists %I on public.%I', target_table || '_set_updated_at', target_table);
    execute format(
      'create trigger %I before update on public.%I for each row execute function public.set_mrkarir_updated_at()',
      target_table || '_set_updated_at',
      target_table
    );
  end loop;
end
$$;

comment on table public.job_sources is 'Compliance-aware registry. API secrets must remain in server or Edge Function secrets, never in this table.';
comment on column public.jobs.is_verified is 'Legacy field. Do not display company verification unless the company itself has been independently verified.';
comment on column public.jobs.verification_status is 'Publishing workflow status; verified_source confirms the source, not the employer.';

