do $$
declare
  public_table_count integer;
  public_tables_without_rls text[];
  migration_count integer;
begin
  select count(*)
  into public_table_count
  from pg_class c
  join pg_namespace n on n.oid = c.relnamespace
  where n.nspname = 'public' and c.relkind = 'r';

  if public_table_count < 20 then
    raise exception 'Expected at least 20 public tables, found %', public_table_count;
  end if;

  select array_agg(c.relname order by c.relname)
  into public_tables_without_rls
  from pg_class c
  join pg_namespace n on n.oid = c.relnamespace
  where n.nspname = 'public'
    and c.relkind = 'r'
    and not c.relrowsecurity;

  if public_tables_without_rls is not null then
    raise exception 'Public tables without RLS: %', public_tables_without_rls;
  end if;

  select count(*)
  into migration_count
  from supabase_migrations.schema_migrations;

  if migration_count <> 13 then
    raise exception 'Expected 13 migrations, found %', migration_count;
  end if;

  if to_regclass('public.jobs') is null then
    raise exception 'public.jobs is missing';
  end if;

  if to_regprocedure('public.expire_jobs_safely()') is null then
    raise exception 'public.expire_jobs_safely() is missing';
  end if;
end
$$;
