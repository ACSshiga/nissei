-- 既存のmaterialsテーブルを削除して資料管理用に再作成

-- 既存テーブルの削除（依存関係があるため先にFK制約を削除）
DROP TABLE IF EXISTS materials CASCADE;
DROP TABLE IF EXISTS material_categories CASCADE;

-- 資料管理用materialsテーブルの作成
CREATE TABLE materials (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  title VARCHAR(200) NOT NULL,
  machine_no VARCHAR(100),
  model VARCHAR(100),
  scope VARCHAR(20) NOT NULL,
  series VARCHAR(50) NOT NULL,
  tonnage INTEGER,
  file_path VARCHAR(500) NOT NULL,
  file_size BIGINT,
  uploaded_by UUID REFERENCES users(id) ON DELETE SET NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX idx_materials_scope ON materials(scope);
CREATE INDEX idx_materials_machine_no ON materials(machine_no);
CREATE INDEX idx_materials_model ON materials(model);
CREATE INDEX idx_materials_series_tonnage ON materials(series, tonnage);

COMMENT ON TABLE materials IS '資料管理テーブル（4段階スコープ：machine/model/tonnage/series）';
COMMENT ON COLUMN materials.scope IS 'スコープレベル: machine, model, tonnage, series';
COMMENT ON COLUMN materials.machine_no IS '特定機番（scope=machineの場合）';
COMMENT ON COLUMN materials.model IS '特定機種（scope=modelの場合）';
COMMENT ON COLUMN materials.series IS 'シリーズ名（NEX, HMX等）';
COMMENT ON COLUMN materials.tonnage IS 'トン数（scope=tonnageの場合）';
