alter table public.user_profiles
  add column if not exists public_email text,
  add column if not exists linkedin_url text,
  add column if not exists github_url text,
  add column if not exists education jsonb not null default '[]'::jsonb,
  add column if not exists experiences jsonb not null default '[]'::jsonb,
  add column if not exists skills text[] not null default '{}',
  add column if not exists certifications jsonb not null default '[]'::jsonb,
  add column if not exists languages jsonb not null default '[]'::jsonb;

create table if not exists public.source_integrations (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  provider text not null check (provider in ('github','gmail','cloudflare')),
  external_account_id text,
  account_email text,
  display_name text,
  avatar_url text,
  sync_enabled boolean not null default false,
  last_synced_at timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (user_id, provider)
);

alter table public.source_integrations enable row level security;
grant select, insert, update, delete on public.source_integrations to authenticated;
drop policy if exists "source_integrations_owner_all" on public.source_integrations;
create policy "source_integrations_owner_all"
  on public.source_integrations for all to authenticated
  using ((select auth.uid()) = user_id)
  with check ((select auth.uid()) = user_id);

create index if not exists source_integrations_user_idx
  on public.source_integrations (user_id, provider);

