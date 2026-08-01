-- Clearly labeled demonstration jobs. These are not real vacancies.
insert into public.jobs (
  external_id, source, source_url, apply_url, title, company_name, location, country,
  work_system, employment_type, experience_level, education_level,
  salary_min, salary_max, salary_currency, salary_period, salary_is_visible,
  description, requirements, skills, benefits, published_at, expires_at,
  is_active, is_verified, is_demo, apply_url_checked_at
) values
('demo-remote-chat-support','mrkarir_demo','https://mrkarirai.web.id/tentang-kami',null,'Remote Chat Support','NusaConnect Labs (Fiktif)','Indonesia','Indonesia','remote','full_time','entry','SMA/SMK',5000000,7000000,'IDR','month',true,'Data Contoh — bukan lowongan nyata. Digunakan untuk mendemonstrasikan pencarian, penyimpanan, dan tracker.','{"Komunikasi tertulis","Terbiasa menggunakan komputer"}','{"Bahasa Indonesia","Live Chat","CRM"}','{"Jadwal fleksibel"}',now(),now() + interval '180 days',true,false,true,now()),
('demo-email-support','mrkarir_demo','https://mrkarirai.web.id/tentang-kami',null,'Email Support Specialist','BrightDesk Asia (Fiktif)','Kuala Lumpur, Malaysia','Malaysia','remote','full_time','entry','SMA/SMK',500,750,'USD','month',true,'Data Contoh — bukan lowongan nyata.','{"Bahasa Inggris tertulis","Layanan pelanggan"}','{"Email Support","English","Zendesk"}','{"Kerja remote"}',now() - interval '2 hours',now() + interval '180 days',true,false,true,now()),
('demo-data-entry','mrkarir_demo','https://mrkarirai.web.id/tentang-kami',null,'Data Entry Operator','Aksara Dataworks (Fiktif)','Jakarta, Indonesia','Indonesia','hybrid','contract','no_experience','SMA/SMK',4800000,6000000,'IDR','month',true,'Data Contoh — bukan lowongan nyata.','{"Teliti","Mampu bekerja dengan target"}','{"Excel","Data Entry","Quality Check"}','{"Pelatihan internal"}',now() - interval '4 hours',now() + interval '180 days',true,false,true,now()),
('demo-virtual-assistant','mrkarir_demo','https://mrkarirai.web.id/tentang-kami',null,'Virtual Assistant','OrbitAssist Co. (Fiktif)','Singapore','Singapore','remote','freelance','entry','Diploma',6,9,'USD','hour',true,'Data Contoh — bukan lowongan nyata.','{"Manajemen waktu","Bahasa Inggris"}','{"Calendar","Notion","Research"}','{"Jam fleksibel"}',now() - interval '6 hours',now() + interval '180 days',true,false,true,now()),
('demo-it-support','mrkarir_demo','https://mrkarirai.web.id/tentang-kami',null,'Junior IT Support','Sagara Teknologi (Fiktif)','Bandung, Indonesia','Indonesia','onsite','full_time','fresh_graduate','Diploma',5000000,7500000,'IDR','month',true,'Data Contoh — bukan lowongan nyata.','{"Dasar komputer","Siap bekerja onsite"}','{"Windows","Networking","Helpdesk"}','{"Asuransi dasar"}',now() - interval '1 day',now() + interval '180 days',true,false,true,now()),
('demo-network-support','mrkarir_demo','https://mrkarirai.web.id/tentang-kami',null,'Network Support Associate','LintasNet Digital (Fiktif)','Surabaya, Indonesia','Indonesia','hybrid','full_time','entry','Diploma',6000000,9000000,'IDR','month',true,'Data Contoh — bukan lowongan nyata.','{"Jaringan dasar","Troubleshooting"}','{"TCP/IP","MikroTik","CCNA"}','{"Anggaran sertifikasi"}',now() - interval '1 day',now() + interval '180 days',true,false,true,now()),
('demo-content-writer','mrkarir_demo','https://mrkarirai.web.id/tentang-kami',null,'Content Writer Indonesia','CeritaKita Studio (Fiktif)','Indonesia','Indonesia','remote','part_time','entry','SMA/SMK',3000000,5000000,'IDR','month',true,'Data Contoh — bukan lowongan nyata.','{"Portfolio tulisan","Riset mandiri"}','{"SEO","Writing","Research"}','{"Kerja remote"}',now() - interval '2 days',now() + interval '180 days',true,false,true,now()),
('demo-transcription','mrkarir_demo','https://mrkarirai.web.id/tentang-kami',null,'Indonesian Transcriptionist','VerbaCloud (Fiktif)','Global','Global','remote','freelance','no_experience','SMA/SMK',8,12,'USD','hour',true,'Data Contoh — bukan lowongan nyata.','{"Bahasa Indonesia","Pendengaran baik"}','{"Transcription","Bahasa","Listening"}','{"Jadwal mandiri"}',now() - interval '2 days',now() + interval '180 days',true,false,true,now()),
('demo-subtitle-reviewer','mrkarir_demo','https://mrkarirai.web.id/tentang-kami',null,'Subtitle Reviewer','LinguaFrame Media (Fiktif)','Global','Global','remote','contract','entry','Diploma',10,14,'USD','hour',true,'Data Contoh — bukan lowongan nyata.','{"Ketelitian bahasa","Bahasa Inggris"}','{"Subtitle","Quality Control","English"}','{"Jam fleksibel"}',now() - interval '3 days',now() + interval '180 days',true,false,true,now()),
('demo-junior-web-developer','mrkarir_demo','https://mrkarirai.web.id/tentang-kami',null,'Junior Web Developer','KodeRuang Labs (Fiktif)','Yogyakarta, Indonesia','Indonesia','hybrid','full_time','fresh_graduate','Diploma',6000000,10000000,'IDR','month',true,'Data Contoh — bukan lowongan nyata.','{"Portfolio web","Dasar JavaScript"}','{"React","TypeScript","Git"}','{"Mentoring"}',now() - interval '3 days',now() + interval '180 days',true,false,true,now()),
('demo-administrative-assistant','mrkarir_demo','https://mrkarirai.web.id/tentang-kami',null,'Administrative Assistant','Pilar Kerja Nusantara (Fiktif)','Palembang, Indonesia','Indonesia','onsite','full_time','entry','SMA/SMK',4500000,6000000,'IDR','month',true,'Data Contoh — bukan lowongan nyata.','{"Administrasi dasar","Komunikasi"}','{"Microsoft Office","Filing","Communication"}','{"Makan siang"}',now() - interval '4 days',now() + interval '180 days',true,false,true,now()),
('demo-customer-support','mrkarir_demo','https://mrkarirai.web.id/tentang-kami',null,'Customer Support Agent','HaloSahabat Global (Fiktif)','Indonesia','Indonesia','remote','full_time','entry','SMA/SMK',5000000,8000000,'IDR','month',true,'Data Contoh — bukan lowongan nyata.','{"Empati","Komunikasi"}','{"Chat","Email","Customer Service"}','{"Kerja remote"}',now() - interval '4 days',now() + interval '180 days',true,false,true,now())
on conflict (source, external_id) do update set
  title = excluded.title,
  company_name = excluded.company_name,
  location = excluded.location,
  description = excluded.description,
  requirements = excluded.requirements,
  skills = excluded.skills,
  benefits = excluded.benefits,
  is_active = true,
  is_demo = true,
  updated_at = now();

