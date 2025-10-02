-- projectsテーブルに management_no と machine_no を追加
ALTER TABLE projects ADD COLUMN IF NOT EXISTS management_no VARCHAR(50);
ALTER TABLE projects ADD COLUMN IF NOT EXISTS machine_no VARCHAR(100);

-- 既存データの更新（nameから抽出）
UPDATE projects
SET
  management_no = SPLIT_PART(name, ' (', 1),
  machine_no = CASE
    WHEN POSITION(' (' IN name) > 0 THEN TRIM(TRAILING ')' FROM SPLIT_PART(name, ' (', 2))
    ELSE ''
  END
WHERE management_no IS NULL;
