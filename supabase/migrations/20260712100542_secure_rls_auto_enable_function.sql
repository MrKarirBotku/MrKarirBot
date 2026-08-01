-- The production project had this legacy helper when the original migration ran,
-- but a fresh Supabase database does not. Keep the hardening operation idempotent
-- so the recovered migration history can also bootstrap an empty database.
do $$
begin
  if to_regprocedure('public.rls_auto_enable()') is not null then
    revoke execute on function public.rls_auto_enable() from public, anon, authenticated;
  end if;
end;
$$;
