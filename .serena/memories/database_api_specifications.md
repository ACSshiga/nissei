# データベース・API仕様（2025-10-02最終確定）

**最終更新**: 2025-10-02

## データベース全体設計

### プラットフォーム
- Supabase PostgreSQL 15
- プロジェクトID: wwyrthkizkcgndyorcww

---

## 📊 全テーブル一覧

### ユーザー・認証

1. **users** - ユーザー

### 案件管理

2. **projects** - 案件
3. **work_logs** - 工数入力

### 資料管理

4. **materials** - 資料

### マスタデータ

5. **master_work_category** - 作業区分マスタ
6. **master_kishyu** - 機種マスタ
7. **master_nounyusaki** - 納入先マスタ
8. **master_shinchoku** - 進捗マスタ

### 注意点リスト

9. **master_chuiten_category** - 注意点カテゴリマスタ
10. **master_chuiten** - 注意点マスタ

### 請求書

11. **invoices** - 請求書
12. **invoice_items** - 請求書明細

---

## 📋 詳細テーブル定義

### 1. users（ユーザー）

```sql
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email VARCHAR(255) UNIQUE NOT NULL,
  username VARCHAR(100) NOT NULL,
  hashed_password VARCHAR(255) NOT NULL,
  role VARCHAR(20) DEFAULT 'worker',     -- 'worker' | 'admin'
  color VARCHAR(7),                      -- 担当者色分け用（例: #FF0000）
  is_active BOOLEAN DEFAULT true,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);
```

---

### 2. projects（案件）

```sql
CREATE TABLE projects (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  management_no VARCHAR(50) UNIQUE NOT NULL,     -- 管理No: E25A001
  machine_no VARCHAR(100) NOT NULL,              -- 機番
  model VARCHAR(100) NOT NULL,                   -- 機種: NEX140Ⅲ
  spec_code VARCHAR(50),                         -- 仕様コード: 24AK
  full_model_name VARCHAR(200),                  -- 表示用: NEX140Ⅲ-24AK
  
  work_category_id UUID REFERENCES master_work_category(id),  -- 作業区分
  delivery_destination_id UUID REFERENCES master_nounyusaki(id), -- 納入先
  assignee_id UUID REFERENCES users(id),         -- 担当者
  progress_id UUID REFERENCES master_shinchoku(id), -- 進捗
  
  planned_hours DECIMAL(10,2),                   -- 予定工数（時間）
  deadline DATE,                                 -- 作図期限
  started_at TIMESTAMP,                          -- 仕掛日
  completed_at TIMESTAMP,                        -- 完了日
  
  -- メモフィールド
  reference_code VARCHAR(200),                   -- 参考製番
  circuit_diagram_no VARCHAR(200),               -- 回路図番
  delay_reason TEXT,                             -- 係り超過理由
  notes TEXT,                                    -- 備考
  
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_projects_management_no ON projects(management_no);
CREATE INDEX idx_projects_assignee ON projects(assignee_id);
CREATE INDEX idx_projects_progress ON projects(progress_id);
CREATE INDEX idx_projects_deadline ON projects(deadline);
CREATE INDEX idx_projects_model ON projects(model);
```

---

### 3. work_logs（工数入力）

```sql
CREATE TABLE work_logs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  work_date DATE NOT NULL,
  start_time TIME,
  end_time TIME,
  duration_minutes INTEGER NOT NULL,             -- 15分刻み
  work_content TEXT,                             -- 作業内容メモ
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_work_logs_project ON work_logs(project_id);
CREATE INDEX idx_work_logs_user ON work_logs(user_id);
CREATE INDEX idx_work_logs_date ON work_logs(work_date);
CREATE INDEX idx_work_logs_project_date ON work_logs(project_id, work_date);
```

---

### 4. materials（資料）

```sql
CREATE TABLE materials (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  title VARCHAR(200) NOT NULL,
  machine_no VARCHAR(100),                       -- 案件固有の場合のみ
  model VARCHAR(100),                            -- 機種: NEX140Ⅲ
  scope VARCHAR(20) NOT NULL,                    -- 'machine' | 'model' | 'tonnage' | 'series'
  series VARCHAR(50) NOT NULL,
  tonnage INTEGER,
  file_path VARCHAR(500) NOT NULL,               -- Supabase Storage内のパス
  file_size BIGINT,
  uploaded_by UUID REFERENCES users(id),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_materials_scope_series ON materials(scope, series);
CREATE INDEX idx_materials_machine_no ON materials(machine_no) WHERE machine_no IS NOT NULL;
CREATE INDEX idx_materials_model ON materials(model) WHERE model IS NOT NULL;
```

---

### 5. master_work_category（作業区分マスタ）

```sql
CREATE TABLE master_work_category (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(100) UNIQUE NOT NULL,             -- 盤配, 線加工
  sort_order INTEGER DEFAULT 0,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 初期データ
INSERT INTO master_work_category (name, sort_order) VALUES
  ('盤配', 1),
  ('線加工', 2);
```

---

### 6. master_kishyu（機種マスタ）

```sql
CREATE TABLE master_kishyu (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  model VARCHAR(100) UNIQUE NOT NULL,            -- 機種名: NEX140Ⅲ
  series VARCHAR(50) NOT NULL,                   -- シリーズ: NEX
  tonnage INTEGER NOT NULL,                      -- トン数: 140
  generation VARCHAR(10) NOT NULL,               -- 世代: Ⅲ
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_kishyu_series ON master_kishyu(series);
CREATE INDEX idx_kishyu_tonnage ON master_kishyu(series, tonnage);
```

---

### 7. master_nounyusaki（納入先マスタ）

```sql
CREATE TABLE master_nounyusaki (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(100) UNIQUE NOT NULL,             -- A社、B社
  code VARCHAR(50),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**自動追加**: PDF取り込み時に新しい納入先を自動マスタ化

---

### 8. master_shinchoku（進捗マスタ）

```sql
CREATE TABLE master_shinchoku (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(100) NOT NULL,                    -- 未着手、作図中、完成(A社)
  code VARCHAR(50) UNIQUE NOT NULL,
  background_color VARCHAR(7),                   -- 背景色: #FF0000
  is_completed BOOLEAN DEFAULT false,            -- 完了フラグ（請求書生成用）
  sort_order INTEGER DEFAULT 0,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

### 9. master_chuiten_category（注意点カテゴリマスタ）

```sql
CREATE TABLE master_chuiten_category (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(100) UNIQUE NOT NULL,             -- A板, B板, シーケンサ, etc
  sort_order INTEGER DEFAULT 0,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 初期データ（資料作成注意点一覧.csvから抽出）
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
```

---

### 10. master_chuiten（注意点マスタ）

```sql
CREATE TABLE master_chuiten (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  seq_no INTEGER UNIQUE NOT NULL,                -- 連番 (1, 2, 3...)
  target_series VARCHAR(100),                    -- 対象シリーズ: 'TNX', 'FNX'
  target_model_pattern VARCHAR(100),             -- 対象機種パターン: 'TC15～', 'NEX30'
  category_id UUID REFERENCES master_chuiten_category(id),
  note TEXT NOT NULL,                            -- 注意点・留意点
  author VARCHAR(100),                           -- 記入者
  remarks TEXT,                                  -- 備考
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_chuiten_series ON master_chuiten(target_series);
CREATE INDEX idx_chuiten_category ON master_chuiten(category_id);
```

---

### 11. invoices（請求書）

```sql
CREATE TABLE invoices (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  year_month VARCHAR(7) NOT NULL,                -- 例: '2025-08'
  file_path VARCHAR(500),                        -- 生成されたExcelファイルのパス
  created_by UUID REFERENCES users(id),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_invoices_year_month ON invoices(year_month);
```

---

### 12. invoice_items（請求書明細）

```sql
CREATE TABLE invoice_items (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  invoice_id UUID NOT NULL REFERENCES invoices(id) ON DELETE CASCADE,
  project_id UUID NOT NULL REFERENCES projects(id),
  management_no VARCHAR(50) NOT NULL,            -- 管理No
  machine_no VARCHAR(100) NOT NULL,              -- 委託業務内容（機番）
  actual_hours DECIMAL(10,2) NOT NULL,           -- 実工数（時間）
  sort_order INTEGER DEFAULT 0
);

CREATE INDEX idx_invoice_items_invoice ON invoice_items(invoice_id);
```

---

## 🔌 主要API設計

### 認証

```
POST   /api/auth/register          ユーザー登録
POST   /api/auth/login             ログイン
GET    /api/users/me               現在のユーザー情報取得
```

---

### 案件管理

```
GET    /api/projects                案件一覧（検索・フィルタ）
POST   /api/projects                案件作成
GET    /api/projects/:id            案件詳細
PUT    /api/projects/:id            案件更新
DELETE /api/projects/:id            案件削除
```

---

### 工数管理

```
GET    /api/worklogs/grid?month=YYYY-MM  月グリッドデータ取得
PUT    /api/worklogs/grid                差分パッチ更新
POST   /api/worklogs                     工数個別登録
GET    /api/worklogs/summary             集計データ取得
```

---

### 資料管理

```
POST   /api/materials/project/:projectId/upload    案件の資料アップロード（複数）
POST   /api/materials/upload                        機種別資料アップロード（複数）
GET    /api/materials/project/:projectId            案件の資料一覧（4段階表示）
GET    /api/materials/:id/download                  資料ダウンロードURL取得
PUT    /api/materials/:id                           資料編集（タイトル・scope変更）
DELETE /api/materials/:id                           資料削除
```

---

### 注意点リスト

```
GET    /api/chuiten                                  注意点一覧（フィルタ・検索）
POST   /api/chuiten                                  注意点追加
PUT    /api/chuiten/:id                              注意点更新
DELETE /api/chuiten/:id                              注意点削除
GET    /api/chuiten/categories                       カテゴリマスタ一覧
GET    /api/projects/:id/chuiten                     案件関連の注意点
```

---

### 請求書

```
GET    /api/invoices?month=YYYY-MM                   請求プレビュー
POST   /api/invoices/generate                        請求書Excel生成
GET    /api/invoices/:id                             請求書詳細
```

---

### マスタ管理

```
GET    /api/masters/work-categories    作業区分マスタ
GET    /api/masters/kishyu              機種マスタ
GET    /api/masters/nounyusaki          納入先マスタ
GET    /api/masters/shinchoku           進捗マスタ
POST   /api/masters/:type               マスタ追加
PUT    /api/masters/:type/:id           マスタ更新
```

---

## 📝 重要な仕様

### 機種のパース処理

```python
import re

def parse_full_model_name(full_name):
    """
    例: NEX140Ⅲ-24AK → {
        'model': 'NEX140Ⅲ',
        'series': 'NEX',
        'tonnage': 140,
        'generation': 'Ⅲ',
        'spec_code': '24AK'
    }
    """
    # 正規表現: シリーズ + トン数 + 世代 (+ オプションで仕様コード)
    pattern = r'([A-Z]+)(\d+)(Ⅰ|Ⅱ|Ⅲ|Ⅳ|Ⅴ|Ⅵ)(?:-(.+))?'
    match = re.match(pattern, normalize_string(full_name))
    
    if not match:
        raise ValueError(f"Invalid model name: {full_name}")
    
    series, tonnage, generation, spec_code = match.groups()
    
    model = f"{series}{tonnage}{generation}"  # NEX140Ⅲ
    
    return {
        'model': model,
        'series': series,
        'tonnage': int(tonnage),
        'generation': generation,
        'spec_code': spec_code or ''
    }
```

---

### 資料の自動集約（案件詳細）

```python
def get_materials_for_project(project_id):
    project = get_project(project_id)
    parsed = parse_full_model_name(project.full_model_name)
    
    return {
        'machine': Material.filter(machine_no=project.machine_no),
        'model': Material.filter(model=parsed['model']),      # NEX140Ⅲ
        'tonnage': Material.filter(
            series=parsed['series'], 
            tonnage=parsed['tonnage']
        ),
        'series': Material.filter(series=parsed['series'])
    }
```

---

## 🗂️ データ整合性ルール

1. **工数の実績自動集計**: projects.actual_hoursは手動編集不可（work_logsから自動集計）
2. **進捗変更トリガー**: 進捗変更時、started_at/completed_atを自動設定
3. **機種の正規化**: 機番取り込み時、機種名を自動パース＆機種マスタ照合
4. **納入先の自動マスタ化**: PDF取り込み時、新しい納入先を自動追加

---

## 📊 削除されたテーブル・機能

以下は実装しない：

- ~~checklists（チェックリスト）~~ → 注意点リストに統合
- ~~material_categories（資料カテゴリマスタ）~~ → 不要
- ~~pdf_import_logs（PDFインポートログ）~~ → Phase 2以降
- ~~master_toiawase（問い合わせマスタ）~~ → 不要（確認済み）
