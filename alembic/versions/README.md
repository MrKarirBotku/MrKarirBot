Produksi menggunakan migration history Supabase yang sudah ada. Migration awal lama
dihapus karena membuat tabel paralel (`users`, integer `jobs.id`, dan tabel tracker lama)
yang tidak kompatibel dengan schema Supabase aktif.

Perubahan produksi baru disimpan di `supabase/migrations/` dan selalu disertai rollback
di `supabase/rollback/`. Jangan menjalankan `alembic upgrade` terhadap database produksi.
