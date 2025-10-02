-- マスタテーブルの作成

-- 1. 作業区分マスタ
CREATE TABLE IF NOT EXISTS master_work_category (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(100) NOT NULL,
  sort_order INTEGER DEFAULT 0 NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_master_work_category_sort ON master_work_category(sort_order);

-- 初期データ
INSERT INTO master_work_category (name, sort_order) VALUES
  ('盤配', 1),
  ('線加工', 2)
ON CONFLICT DO NOTHING;

-- 2. 機種マスタ
CREATE TABLE IF NOT EXISTS master_kishyu (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  series VARCHAR(50) NOT NULL,
  tonnage INTEGER,
  generation VARCHAR(20),
  model_name VARCHAR(100) NOT NULL,
  is_active BOOLEAN DEFAULT true NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_master_kishyu_series_tonnage ON master_kishyu(series, tonnage);
CREATE INDEX IF NOT EXISTS idx_master_kishyu_model_name ON master_kishyu(model_name);

COMMENT ON TABLE master_kishyu IS '機種マスタ';
COMMENT ON COLUMN master_kishyu.model_name IS '機種名 = シリーズ + トン数 + 世代（例: NEX140Ⅲ）';

-- 3. 納入先マスタ
CREATE TABLE IF NOT EXISTS master_nounyusaki (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(200) NOT NULL,
  code VARCHAR(50),
  sort_order INTEGER DEFAULT 0 NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_master_nounyusaki_sort ON master_nounyusaki(sort_order);

-- 4. 進捗マスタ
CREATE TABLE IF NOT EXISTS master_shinchoku (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(100) NOT NULL,
  sort_order INTEGER DEFAULT 0 NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_master_shinchoku_sort ON master_shinchoku(sort_order);

-- 初期データ例
INSERT INTO master_shinchoku (name, sort_order) VALUES
  ('受注済み', 1),
  ('作図中', 2),
  ('完成', 3),
  ('出荷済み', 4)
ON CONFLICT DO NOTHING;

-- 5. 注意点カテゴリマスタ
CREATE TABLE IF NOT EXISTS master_chuiten_category (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(100) NOT NULL,
  sort_order INTEGER DEFAULT 0 NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_master_chuiten_category_sort ON master_chuiten_category(sort_order);

-- 初期データ例
INSERT INTO master_chuiten_category (name, sort_order) VALUES
  ('A板', 1),
  ('B板', 2),
  ('C板', 3),
  ('D板', 4),
  ('シーケンサ', 5),
  ('アンプBOX', 6),
  ('制御BOXカバーA', 7),
  ('回路図', 8),
  ('端子台', 9)
ON CONFLICT DO NOTHING;

-- 6. 注意点マスタ
CREATE TABLE IF NOT EXISTS master_chuiten (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  category_id UUID REFERENCES master_chuiten_category(id) ON DELETE SET NULL,
  target_series VARCHAR(100),
  target_board VARCHAR(100),
  content TEXT NOT NULL,
  author VARCHAR(100),
  notes TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_master_chuiten_category ON master_chuiten(category_id);
CREATE INDEX IF NOT EXISTS idx_master_chuiten_target_series ON master_chuiten(target_series);

COMMENT ON TABLE master_chuiten IS '注意点マスタ（チェックリストではなく注意点リスト）';
