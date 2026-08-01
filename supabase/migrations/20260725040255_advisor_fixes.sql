-- Advisor fixes after complete product migration.
create index if not exists contact_messages_user_idx on public.contact_messages (user_id);

drop policy if exists "articles_admin_write" on public.articles;
drop policy if exists "articles_admin_insert" on public.articles;
create policy "articles_admin_insert" on public.articles for insert to authenticated
  with check (coalesce((select auth.jwt()) -> 'app_metadata' ->> 'role', '') in ('admin','super_admin'));
drop policy if exists "articles_admin_update" on public.articles;
create policy "articles_admin_update" on public.articles for update to authenticated
  using (coalesce((select auth.jwt()) -> 'app_metadata' ->> 'role', '') in ('admin','super_admin'))
  with check (coalesce((select auth.jwt()) -> 'app_metadata' ->> 'role', '') in ('admin','super_admin'));
drop policy if exists "articles_admin_delete" on public.articles;
create policy "articles_admin_delete" on public.articles for delete to authenticated
  using (coalesce((select auth.jwt()) -> 'app_metadata' ->> 'role', '') in ('admin','super_admin'));

drop policy if exists "learning_materials_admin_write" on public.learning_materials;
drop policy if exists "learning_materials_admin_insert" on public.learning_materials;
create policy "learning_materials_admin_insert" on public.learning_materials for insert to authenticated
  with check (coalesce((select auth.jwt()) -> 'app_metadata' ->> 'role', '') in ('admin','super_admin'));
drop policy if exists "learning_materials_admin_update" on public.learning_materials;
create policy "learning_materials_admin_update" on public.learning_materials for update to authenticated
  using (coalesce((select auth.jwt()) -> 'app_metadata' ->> 'role', '') in ('admin','super_admin'))
  with check (coalesce((select auth.jwt()) -> 'app_metadata' ->> 'role', '') in ('admin','super_admin'));
drop policy if exists "learning_materials_admin_delete" on public.learning_materials;
create policy "learning_materials_admin_delete" on public.learning_materials for delete to authenticated
  using (coalesce((select auth.jwt()) -> 'app_metadata' ->> 'role', '') in ('admin','super_admin'));

