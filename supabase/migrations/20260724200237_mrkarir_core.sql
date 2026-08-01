-- MrKarir AI core schema. All user-owned tables are protected with RLS.
create extension if not exists pgcrypto;

create table if not exists public.user_profiles (
  id uuid primary key references auth.users(id) on delete cascade,
  full_name text,
  headline text,
  about text,
  location text,
  target_roles text[] not null default '{}',
  preferred_work_modes text[] not null default '{}',
  expected_salary_min numeric,
  expected_salary_max numeric,
  salary_currency text not null default 'IDR',
  profile_visibility text not null default 'private'
    check (profile_visibility in ('private', 'public')),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.saved_jobs (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  job_key text not null,
  job_title text not null,
  company_name text not null,
  job_location text,
  job_mode text,
  source_url text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (user_id, job_key)
);

create table if not exists public.job_applications (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  job_key text,
  position text not null,
  company text not null,
  location text,
  source_url text,
  salary text,
  status text not null default 'saved'
    check (status in ('saved','planning','applied','test','interview','waiting','accepted','rejected')),
  applied_at date,
  test_at timestamptz,
  interview_at timestamptz,
  recruiter_contact text,
  notes text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.resumes (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  title text not null default 'CV Utama',
  target_role text,
  content jsonb not null default '{}'::jsonb,
  ats_score integer check (ats_score between 0 and 100),
  is_primary boolean not null default false,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index if not exists saved_jobs_user_created_idx on public.saved_jobs (user_id, created_at desc);
create index if not exists applications_user_status_idx on public.job_applications (user_id, status);
create index if not exists applications_user_interview_idx on public.job_applications (user_id, interview_at) where interview_at is not null;
create index if not exists resumes_user_updated_idx on public.resumes (user_id, updated_at desc);

alter table public.user_profiles enable row level security;
alter table public.saved_jobs enable row level security;
alter table public.job_applications enable row level security;
alter table public.resumes enable row level security;

grant select, insert, update, delete on public.user_profiles to authenticated;
grant select, insert, update, delete on public.saved_jobs to authenticated;
grant select, insert, update, delete on public.job_applications to authenticated;
grant select, insert, update, delete on public.resumes to authenticated;

drop policy if exists "profiles_select_own" on public.user_profiles;
create policy "profiles_select_own" on public.user_profiles for select to authenticated using ((select auth.uid()) = id);
drop policy if exists "profiles_insert_own" on public.user_profiles;
create policy "profiles_insert_own" on public.user_profiles for insert to authenticated with check ((select auth.uid()) = id);
drop policy if exists "profiles_update_own" on public.user_profiles;
create policy "profiles_update_own" on public.user_profiles for update to authenticated using ((select auth.uid()) = id) with check ((select auth.uid()) = id);
drop policy if exists "profiles_delete_own" on public.user_profiles;
create policy "profiles_delete_own" on public.user_profiles for delete to authenticated using ((select auth.uid()) = id);

drop policy if exists "saved_jobs_owner_all" on public.saved_jobs;
create policy "saved_jobs_owner_all" on public.saved_jobs for all to authenticated using ((select auth.uid()) = user_id) with check ((select auth.uid()) = user_id);
drop policy if exists "applications_owner_all" on public.job_applications;
create policy "applications_owner_all" on public.job_applications for all to authenticated using ((select auth.uid()) = user_id) with check ((select auth.uid()) = user_id);
drop policy if exists "resumes_owner_all" on public.resumes;
create policy "resumes_owner_all" on public.resumes for all to authenticated using ((select auth.uid()) = user_id) with check ((select auth.uid()) = user_id);

create or replace function public.handle_new_mrkarir_user()
returns trigger language plpgsql security definer set search_path = ''
as $$
begin
  insert into public.user_profiles (id, full_name)
  values (new.id, nullif(new.raw_user_meta_data ->> 'full_name', ''))
  on conflict (id) do nothing;
  return new;
end;
$$;
revoke all on function public.handle_new_mrkarir_user() from public;
revoke all on function public.handle_new_mrkarir_user() from anon;
revoke all on function public.handle_new_mrkarir_user() from authenticated;
drop trigger if exists on_auth_user_created_mrkarir on auth.users;
create trigger on_auth_user_created_mrkarir after insert on auth.users
for each row execute function public.handle_new_mrkarir_user();

