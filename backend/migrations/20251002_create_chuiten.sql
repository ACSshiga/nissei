-- 注意点リスト機能のマイグレーション
-- 作成日: 2025-10-02

-- master_chuiten_category（注意点カテゴリマスタ）
CREATE TABLE master_chuiten_category (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(100) UNIQUE NOT NULL,        -- A板, B板, シーケンサ, etc
  sort_order INTEGER DEFAULT 0,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_chuiten_category_sort ON master_chuiten_category(sort_order);

-- 初期データ
INSERT INTO master_chuiten_category (name, sort_order) VALUES
  ('A板', 1),
  ('B板', 2),
  ('C板', 3),
  ('D板', 4),
  ('シーケンサ', 5),
  ('シーケンサ・A板', 6),
  ('アンプBOX', 7),
  ('制御BOXカバーA', 8),
  ('回路図', 9),
  ('端子台', 10),
  ('その他', 99);

-- master_chuiten（注意点マスタ）
CREATE TABLE master_chuiten (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  seq_no INTEGER UNIQUE NOT NULL,                           -- 連番 (1, 2, 3...)
  target_series VARCHAR(100),                               -- 対象シリーズ: 'TNX', 'FNX', etc
  target_model_pattern VARCHAR(100),                        -- 対象機種パターン: 'TC15～', 'NEX30'
  category_id UUID REFERENCES master_chuiten_category(id),
  note TEXT NOT NULL,                                       -- 注意点・留意点
  author VARCHAR(100),                                      -- 記入者
  remarks TEXT,                                             -- 備考
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_chuiten_series ON master_chuiten(target_series);
CREATE INDEX idx_chuiten_category ON master_chuiten(category_id);
CREATE INDEX idx_chuiten_seq_no ON master_chuiten(seq_no);

COMMENT ON TABLE master_chuiten_category IS '注意点カテゴリマスタ';
COMMENT ON TABLE master_chuiten IS '注意点マスタ（資料作成注意点一覧）';
COMMENT ON COLUMN master_chuiten.seq_no IS '連番（1, 2, 3...）';
COMMENT ON COLUMN master_chuiten.target_series IS '対象シリーズ（TNX, FNX等）';
COMMENT ON COLUMN master_chuiten.target_model_pattern IS '対象機種パターン（TC15～, NEX30等）';
