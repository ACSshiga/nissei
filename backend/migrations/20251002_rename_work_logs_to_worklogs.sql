-- work_logsテーブルをworklogsにリネーム（Supabaseスキーマキャッシュ問題の回避）
ALTER TABLE IF EXISTS work_logs RENAME TO worklogs;

-- 外部キー制約も更新
ALTER TABLE IF EXISTS worklogs RENAME CONSTRAINT work_logs_user_id_fkey TO worklogs_user_id_fkey;
ALTER TABLE IF EXISTS worklogs RENAME CONSTRAINT work_logs_project_id_fkey TO worklogs_project_id_fkey;

-- インデックスも更新（存在する場合）
ALTER INDEX IF EXISTS work_logs_pkey RENAME TO worklogs_pkey;
