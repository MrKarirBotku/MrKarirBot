-- Cover all foreign keys used by the aggregator and remove overlapping
-- permissive SELECT policies reported by Supabase advisors.

create index if not exists applications_v2_user_status_idx
  on public.applications (user_id, status, updated_at desc);
create index if not exists applications_v2_job_id_idx
  on public.applications (job_id) where job_id is not null;
create index if not exists applications_v2_resume_id_idx
  on public.applications (resume_id) where resume_id is not null;
create index if not exists companies_verified_by_idx
  on public.companies (verified_by) where verified_by is not null;
create index if not exists company_job_boards_company_id_idx
  on public.company_job_boards (company_id) where company_id is not null;
create index if not exists company_job_boards_verified_by_idx
  on public.company_job_boards (verified_by) where verified_by is not null;
create index if not exists job_alert_deliveries_saved_search_idx
  on public.job_alert_deliveries (saved_search_id, created_at desc);
create index if not exists job_reports_job_id_idx
  on public.job_reports (job_id) where job_id is not null;
create index if not exists job_reports_user_id_idx
  on public.job_reports (user_id, created_at desc) where user_id is not null;
create index if not exists job_reports_reviewed_by_idx
  on public.job_reports (reviewed_by) where reviewed_by is not null;
create index if not exists job_source_payloads_source_id_idx
  on public.job_source_payloads (source_id, fetched_at desc);
create index if not exists jobs_company_id_idx
  on public.jobs (company_id) where company_id is not null;

drop policy if exists "companies_admin_write" on public.companies;
create policy "companies_admin_insert" on public.companies for insert to authenticated
  with check (coalesce((select auth.jwt()) -> 'app_metadata' ->> 'role','') in ('admin','super_admin'));
create policy "companies_admin_update" on public.companies for update to authenticated
  using (coalesce((select auth.jwt()) -> 'app_metadata' ->> 'role','') in ('admin','super_admin'))
  with check (coalesce((select auth.jwt()) -> 'app_metadata' ->> 'role','') in ('admin','super_admin'));
create policy "companies_admin_delete" on public.companies for delete to authenticated
  using (coalesce((select auth.jwt()) -> 'app_metadata' ->> 'role','') in ('admin','super_admin'));

drop policy if exists "job_sources_admin_write" on public.job_sources;
create policy "job_sources_admin_insert" on public.job_sources for insert to authenticated
  with check (coalesce((select auth.jwt()) -> 'app_metadata' ->> 'role','') in ('admin','super_admin'));
create policy "job_sources_admin_update" on public.job_sources for update to authenticated
  using (coalesce((select auth.jwt()) -> 'app_metadata' ->> 'role','') in ('admin','super_admin'))
  with check (coalesce((select auth.jwt()) -> 'app_metadata' ->> 'role','') in ('admin','super_admin'));
create policy "job_sources_admin_delete" on public.job_sources for delete to authenticated
  using (coalesce((select auth.jwt()) -> 'app_metadata' ->> 'role','') in ('admin','super_admin'));

