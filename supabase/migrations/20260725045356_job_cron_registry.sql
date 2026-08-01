-- Safe scheduler registry. Database-only expiry is active immediately.
-- Edge Function schedules remain explicitly gated until a server-only bearer
-- token is stored in Supabase Vault; no public/client token is accepted.

create extension if not exists pg_cron;
create extension if not exists pg_net with schema extensions;

create table if not exists public.job_cron_config (
  id uuid primary key default gen_random_uuid(),
  task_slug text not null unique,
  schedule text not null,
  target_function text not null,
  source_slug text,
  enabled boolean not null default false,
  status text not null default 'waiting_for_server_token'
    check (status in ('active','waiting_for_server_token','disabled','failed')),
  security_note text not null,
  last_run_at timestamptz,
  last_error text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

insert into public.job_cron_config (
  task_slug, schedule, target_function, source_slug, enabled, status, security_note
) values
  ('sync_himalayas','0 * * * *','jobs-sync','himalayas',false,'waiting_for_server_token','Requires a server-only JWT stored in Vault.'),
  ('sync_arbeitnow','17 */2 * * *','jobs-sync','arbeitnow',false,'waiting_for_server_token','Requires a server-only JWT stored in Vault.'),
  ('sync_greenhouse','31 */3 * * *','jobs-sync','greenhouse',false,'waiting_for_server_token','Requires a server-only JWT and verified company boards.'),
  ('sync_lever','43 */3 * * *','jobs-sync','lever',false,'waiting_for_server_token','Requires a server-only JWT and verified company boards.'),
  ('sync_remotive','53 */6 * * *','jobs-sync','remotive',false,'waiting_for_server_token','Requires a server-only JWT stored in Vault.'),
  ('check_job_urls','20 2 * * *','job-url-check',null,false,'waiting_for_server_token','Requires a server-only JWT; stored URLs are validated before fetch.'),
  ('dispatch_job_alerts','10 * * * *','job-alert-dispatch',null,false,'waiting_for_server_token','Requires a server-only JWT; each saved search enforces its own frequency.'),
  ('expire_jobs','5 * * * *','expire_jobs_safely',null,true,'active','Runs a narrow database function; no external credential is required.')
on conflict (task_slug) do update set
  schedule = excluded.schedule,
  target_function = excluded.target_function,
  source_slug = excluded.source_slug,
  security_note = excluded.security_note,
  updated_at = now();

create or replace function public.expire_jobs_safely()
returns integer
language plpgsql
security definer
set search_path = ''
as $$
declare
  affected integer;
begin
  update public.jobs
  set
    is_active = false,
    verification_status = 'expired',
    last_checked_at = now(),
    updated_at = now()
  where is_active
    and expires_at is not null
    and expires_at < now();
  get diagnostics affected = row_count;

  update public.job_cron_config
  set last_run_at = now(), last_error = null, updated_at = now()
  where task_slug = 'expire_jobs';

  return affected;
end;
$$;

revoke all on function public.expire_jobs_safely() from public, anon, authenticated;
grant execute on function public.expire_jobs_safely() to postgres, service_role;

do $$
declare
  existing_job bigint;
begin
  select jobid into existing_job from cron.job where jobname = 'mrkarir-expire-jobs' limit 1;
  if existing_job is not null then
    perform cron.unschedule(existing_job);
  end if;
  perform cron.schedule(
    'mrkarir-expire-jobs',
    '5 * * * *',
    'select public.expire_jobs_safely();'
  );
end
$$;

alter table public.job_cron_config enable row level security;
grant select, insert, update, delete on public.job_cron_config to authenticated;

create policy "job_cron_config_admin_all"
on public.job_cron_config for all
to authenticated
using (coalesce((select auth.jwt()) -> 'app_metadata' ->> 'role','') in ('admin','super_admin'))
with check (coalesce((select auth.jwt()) -> 'app_metadata' ->> 'role','') in ('admin','super_admin'));

drop trigger if exists job_cron_config_set_updated_at on public.job_cron_config;
create trigger job_cron_config_set_updated_at
before update on public.job_cron_config
for each row execute function public.set_mrkarir_updated_at();

