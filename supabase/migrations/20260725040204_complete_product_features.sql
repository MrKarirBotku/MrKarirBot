-- Complete user tools, content, support, and admin persistence for MrKarir AI.
-- Existing safe internal names remain: resumes (CVs) and job_applications (applications).

alter table public.user_profiles
  add column if not exists preferences jsonb not null default '{}'::jsonb,
  add column if not exists portfolio_url text,
  add column if not exists avatar_url text;

create table if not exists public.cover_letters (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  title text not null,
  language text not null default 'indonesia',
  tone text not null default 'formal',
  job_description text,
  content text not null,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.interview_sessions (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  target_role text not null,
  interview_type text not null,
  language text not null default 'id',
  difficulty text not null default 'pemula',
  score integer check (score between 0 and 100),
  transcript jsonb not null default '[]'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.notifications (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  notification_type text not null default 'general',
  title text not null,
  message text not null,
  action_url text,
  read_at timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.articles (
  id uuid primary key default gen_random_uuid(),
  slug text not null unique,
  title text not null,
  excerpt text,
  content text not null,
  category text,
  status text not null default 'draft' check (status in ('draft','published','archived')),
  published_at timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.learning_materials (
  id uuid primary key default gen_random_uuid(),
  path_slug text not null,
  title text not null,
  description text,
  step_order integer not null check (step_order > 0),
  difficulty text not null default 'pemula',
  estimated_hours numeric check (estimated_hours is null or estimated_hours >= 0),
  resource_url text,
  is_free boolean not null default true,
  is_published boolean not null default true,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (path_slug, step_order)
);

create table if not exists public.learning_progress (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  path_slug text not null,
  completed_steps integer[] not null default '{}',
  progress_percent integer not null default 0 check (progress_percent between 0 and 100),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (user_id, path_slug)
);

create table if not exists public.scam_reports (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references auth.users(id) on delete set null,
  company_name text,
  source_url text,
  recruiter_contact text,
  submitted_text text not null,
  risk_level text not null check (risk_level in ('rendah','sedang','tinggi')),
  risk_score integer not null check (risk_score between 0 and 100),
  indicators text[] not null default '{}',
  analysis_note text not null,
  review_status text not null default 'unreviewed' check (review_status in ('unreviewed','reviewing','resolved','dismissed')),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.contact_messages (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references auth.users(id) on delete set null,
  name text not null,
  email text not null,
  subject text not null,
  message text not null,
  status text not null default 'new' check (status in ('new','reviewing','resolved','spam')),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.admin_audit_logs (
  id uuid primary key default gen_random_uuid(),
  admin_user_id uuid references auth.users(id) on delete set null,
  action text not null,
  entity_type text not null,
  entity_id text,
  details jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index if not exists cover_letters_user_updated_idx on public.cover_letters (user_id, updated_at desc);
create index if not exists interview_sessions_user_created_idx on public.interview_sessions (user_id, created_at desc);
create index if not exists notifications_user_unread_idx on public.notifications (user_id, read_at, created_at desc);
create index if not exists articles_status_published_idx on public.articles (status, published_at desc);
create index if not exists learning_materials_path_idx on public.learning_materials (path_slug, step_order);
create index if not exists learning_progress_user_idx on public.learning_progress (user_id, updated_at desc);
create index if not exists scam_reports_user_created_idx on public.scam_reports (user_id, created_at desc);
create index if not exists scam_reports_review_idx on public.scam_reports (review_status, created_at desc);
create index if not exists contact_messages_status_idx on public.contact_messages (status, created_at desc);
create index if not exists admin_audit_logs_admin_created_idx on public.admin_audit_logs (admin_user_id, created_at desc);

alter table public.cover_letters enable row level security;
alter table public.interview_sessions enable row level security;
alter table public.notifications enable row level security;
alter table public.articles enable row level security;
alter table public.learning_materials enable row level security;
alter table public.learning_progress enable row level security;
alter table public.scam_reports enable row level security;
alter table public.contact_messages enable row level security;
alter table public.admin_audit_logs enable row level security;

grant select, insert, update, delete on public.cover_letters to authenticated;
grant select, insert, update, delete on public.interview_sessions to authenticated;
grant select, update, delete on public.notifications to authenticated;
grant select on public.articles to anon, authenticated;
grant insert, update, delete on public.articles to authenticated;
grant select on public.learning_materials to anon, authenticated;
grant insert, update, delete on public.learning_materials to authenticated;
grant select, insert, update, delete on public.learning_progress to authenticated;
grant select, insert on public.scam_reports to authenticated;
grant update, delete on public.scam_reports to authenticated;
grant insert on public.contact_messages to anon, authenticated;
grant select, update, delete on public.contact_messages to authenticated;
grant select, insert on public.admin_audit_logs to authenticated;

drop policy if exists "cover_letters_owner_all" on public.cover_letters;
create policy "cover_letters_owner_all" on public.cover_letters for all to authenticated
  using ((select auth.uid()) = user_id) with check ((select auth.uid()) = user_id);
drop policy if exists "interview_sessions_owner_all" on public.interview_sessions;
create policy "interview_sessions_owner_all" on public.interview_sessions for all to authenticated
  using ((select auth.uid()) = user_id) with check ((select auth.uid()) = user_id);
drop policy if exists "notifications_owner_select" on public.notifications;
create policy "notifications_owner_select" on public.notifications for select to authenticated
  using ((select auth.uid()) = user_id);
drop policy if exists "notifications_owner_update" on public.notifications;
create policy "notifications_owner_update" on public.notifications for update to authenticated
  using ((select auth.uid()) = user_id) with check ((select auth.uid()) = user_id);
drop policy if exists "notifications_owner_delete" on public.notifications;
create policy "notifications_owner_delete" on public.notifications for delete to authenticated
  using ((select auth.uid()) = user_id);
drop policy if exists "articles_public_read" on public.articles;
create policy "articles_public_read" on public.articles for select to anon, authenticated
  using (status = 'published' or coalesce((select auth.jwt()) -> 'app_metadata' ->> 'role', '') in ('admin','super_admin','moderator'));
drop policy if exists "articles_admin_write" on public.articles;
create policy "articles_admin_write" on public.articles for all to authenticated
  using (coalesce((select auth.jwt()) -> 'app_metadata' ->> 'role', '') in ('admin','super_admin'))
  with check (coalesce((select auth.jwt()) -> 'app_metadata' ->> 'role', '') in ('admin','super_admin'));
drop policy if exists "learning_materials_public_read" on public.learning_materials;
create policy "learning_materials_public_read" on public.learning_materials for select to anon, authenticated
  using (is_published or coalesce((select auth.jwt()) -> 'app_metadata' ->> 'role', '') in ('admin','super_admin','moderator'));
drop policy if exists "learning_materials_admin_write" on public.learning_materials;
create policy "learning_materials_admin_write" on public.learning_materials for all to authenticated
  using (coalesce((select auth.jwt()) -> 'app_metadata' ->> 'role', '') in ('admin','super_admin'))
  with check (coalesce((select auth.jwt()) -> 'app_metadata' ->> 'role', '') in ('admin','super_admin'));
drop policy if exists "learning_progress_owner_all" on public.learning_progress;
create policy "learning_progress_owner_all" on public.learning_progress for all to authenticated
  using ((select auth.uid()) = user_id) with check ((select auth.uid()) = user_id);
drop policy if exists "scam_reports_owner_read_insert" on public.scam_reports;
create policy "scam_reports_owner_read_insert" on public.scam_reports for select to authenticated
  using ((select auth.uid()) = user_id or coalesce((select auth.jwt()) -> 'app_metadata' ->> 'role', '') in ('admin','super_admin','moderator'));
drop policy if exists "scam_reports_owner_insert" on public.scam_reports;
create policy "scam_reports_owner_insert" on public.scam_reports for insert to authenticated
  with check ((select auth.uid()) = user_id);
drop policy if exists "scam_reports_admin_update" on public.scam_reports;
create policy "scam_reports_admin_update" on public.scam_reports for update to authenticated
  using (coalesce((select auth.jwt()) -> 'app_metadata' ->> 'role', '') in ('admin','super_admin','moderator'))
  with check (coalesce((select auth.jwt()) -> 'app_metadata' ->> 'role', '') in ('admin','super_admin','moderator'));
drop policy if exists "contact_messages_public_insert" on public.contact_messages;
create policy "contact_messages_public_insert" on public.contact_messages for insert to anon, authenticated
  with check (user_id is null or (select auth.uid()) = user_id);
drop policy if exists "contact_messages_admin_read" on public.contact_messages;
create policy "contact_messages_admin_read" on public.contact_messages for select to authenticated
  using (coalesce((select auth.jwt()) -> 'app_metadata' ->> 'role', '') in ('admin','super_admin','moderator'));
drop policy if exists "contact_messages_admin_update" on public.contact_messages;
create policy "contact_messages_admin_update" on public.contact_messages for update to authenticated
  using (coalesce((select auth.jwt()) -> 'app_metadata' ->> 'role', '') in ('admin','super_admin','moderator'))
  with check (coalesce((select auth.jwt()) -> 'app_metadata' ->> 'role', '') in ('admin','super_admin','moderator'));
drop policy if exists "admin_audit_logs_admin_read" on public.admin_audit_logs;
create policy "admin_audit_logs_admin_read" on public.admin_audit_logs for select to authenticated
  using (coalesce((select auth.jwt()) -> 'app_metadata' ->> 'role', '') in ('admin','super_admin'));
drop policy if exists "admin_audit_logs_admin_insert" on public.admin_audit_logs;
create policy "admin_audit_logs_admin_insert" on public.admin_audit_logs for insert to authenticated
  with check ((select auth.uid()) = admin_user_id and coalesce((select auth.jwt()) -> 'app_metadata' ->> 'role', '') in ('admin','super_admin'));

