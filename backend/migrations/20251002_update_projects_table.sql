-- projectsテーブルを製造業特化型に更新

-- 既存のprojectsテーブルをバックアップ（念のため）
CREATE TABLE IF NOT EXISTS projects_backup AS SELECT * FROM projects;

-- 新しいカラムを追加
ALTER TABLE projects
  ADD COLUMN IF NOT EXISTS spec_code VARCHAR(50),
  ADD COLUMN IF NOT EXISTS full_model_name VARCHAR(200),
  ADD COLUMN IF NOT EXISTS work_category_id UUID REFERENCES master_work_category(id) ON DELETE SET NULL,
  ADD COLUMN IF NOT EXISTS delivery_destination_id UUID REFERENCES master_nounyusaki(id) ON DELETE SET NULL,
  ADD COLUMN IF NOT EXISTS assignee_id UUID REFERENCES users(id) ON DELETE SET NULL,
  ADD COLUMN IF NOT EXISTS progress_id UUID REFERENCES master_shinchoku(id) ON DELETE SET NULL,
  ADD COLUMN IF NOT EXISTS planned_hours DECIMAL(10,2),
  ADD COLUMN IF NOT EXISTS deadline DATE,
  ADD COLUMN IF NOT EXISTS started_at TIMESTAMP,
  ADD COLUMN IF NOT EXISTS completed_at TIMESTAMP,
  ADD COLUMN IF NOT EXISTS reference_code VARCHAR(200),
  ADD COLUMN IF NOT EXISTS circuit_diagram_no VARCHAR(200),
  ADD COLUMN IF NOT EXISTS delay_reason TEXT,
  ADD COLUMN IF NOT EXISTS notes TEXT;

-- 既存カラム名を更新（user_id → assignee_id への移行は後で手動で対応）
-- management_no は既に存在
-- machine_no は既に存在

-- management_no にユニーク制約を追加（存在しない場合）
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint WHERE conname = 'projects_management_no_key'
  ) THEN
    ALTER TABLE projects ADD CONSTRAINT projects_management_no_key UNIQUE (management_no);
  END IF;
END $$;

-- インデックス追加
CREATE INDEX IF NOT EXISTS idx_projects_work_category ON projects(work_category_id);
CREATE INDEX IF NOT EXISTS idx_projects_delivery_destination ON projects(delivery_destination_id);
CREATE INDEX IF NOT EXISTS idx_projects_assignee ON projects(assignee_id);
CREATE INDEX IF NOT EXISTS idx_projects_progress ON projects(progress_id);
CREATE INDEX IF NOT EXISTS idx_projects_deadline ON projects(deadline);

-- コメント追加
COMMENT ON COLUMN projects.management_no IS '管理番号（E252019等、ユニーク）';
COMMENT ON COLUMN projects.machine_no IS '機番（HMX7-CN2等）';
COMMENT ON COLUMN projects.spec_code IS '仕様コード（24AK）';
COMMENT ON COLUMN projects.full_model_name IS 'model + "-" + spec_code（NEX140Ⅲ-24AK）';
COMMENT ON COLUMN projects.planned_hours IS '予定工数（時間単位）';
COMMENT ON COLUMN projects.reference_code IS '参考製番';
COMMENT ON COLUMN projects.circuit_diagram_no IS '回路図番';
COMMENT ON COLUMN projects.delay_reason IS '係り超過理由';

-- 注: 既存の name, description, status, start_date, end_date, estimated_hours, actual_hours カラムは
-- 互換性のため残しておく。新しいアプリでは新しいカラムを使用する。
