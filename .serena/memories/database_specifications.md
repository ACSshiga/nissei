# データベース設計仕様

**最終更新**: 2025-10-02
**バージョン**: v2.0

## データベース構成

- **プラットフォーム**: Supabase (PostgreSQL)
- **プロジェクトID**: wwyrthkizkcgndyorcww
- **バージョン**: PostgreSQL 15
- **ストレージ**: Supabase Storage (本番), MinIO (開発)

---

## 全テーブル一覧（12テーブル）

### コアテーブル（6つ）
1. **users** - ユーザー管理（Supabase Auth連携）
2. **projects** - 案件管理（製造業特化型）
3. **work_logs** - 工数入力（15分刻み）
4. **materials** - 資料管理（スコープベース共有）
5. **invoices** - 請求書ヘッダ
6. **invoice_items** - 請求書明細

### マスタテーブル（6つ）
1. **master_work_category** - 作業区分（盤配/線加工）
2. **master_kishyu** - 機種マスタ
3. **master_nounyusaki** - 納入先マスタ
4. **master_shinchoku** - 進捗マスタ
5. **master_chuiten_category** - 注意点カテゴリ
6. **master_chuiten** - 注意点本体

---

## テーブル詳細定義

### 1. users（ユーザー）

Supabase Auth連携、管理者フラグ付き。

```sql
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email VARCHAR(255) UNIQUE NOT NULL,
  username VARCHAR(100) NOT NULL,
  hashed_password VARCHAR(255) NOT NULL,
  is_active BOOLEAN DEFAULT true NOT NULL,
  is_admin BOOLEAN DEFAULT false NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE UNIQUE INDEX idx_users_email ON users(email);
```

**フィールド説明**:
- `email`: ログインID（ユニーク）
- `username`: 表示名
- `hashed_password`: bcryptハッシュ化パスワード
- `is_admin`: 管理者権限（請求確定操作等）
- `is_active`: アカウント有効フラグ

---

### 2. projects（案件管理）

製造業特化型、機種・進捗・納入先をマスタで管理。

```sql
CREATE TABLE projects (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  management_no VARCHAR(50) UNIQUE NOT NULL,
  machine_no VARCHAR(100) NOT NULL,
  model VARCHAR(100) NOT NULL,
  spec_code VARCHAR(50),
  full_model_name VARCHAR(200),
  work_category_id UUID REFERENCES master_work_category(id) ON DELETE SET NULL,
  delivery_destination_id UUID REFERENCES master_nounyusaki(id) ON DELETE SET NULL,
  assignee_id UUID REFERENCES users(id) ON DELETE SET NULL,
  progress_id UUID REFERENCES master_shinchoku(id) ON DELETE SET NULL,
  planned_hours DECIMAL(10,2),
  deadline DATE,
  started_at TIMESTAMP,
  completed_at TIMESTAMP,
  reference_code VARCHAR(200),
  circuit_diagram_no VARCHAR(200),
  delay_reason TEXT,
  notes TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE UNIQUE INDEX idx_projects_management_no ON projects(management_no);
CREATE INDEX idx_projects_work_category ON projects(work_category_id);
CREATE INDEX idx_projects_delivery_destination ON projects(delivery_destination_id);
CREATE INDEX idx_projects_assignee ON projects(assignee_id);
CREATE INDEX idx_projects_progress ON projects(progress_id);
CREATE INDEX idx_projects_deadline ON projects(deadline);
```

**重要フィールド**:
- `management_no`: 管理番号（E252019等、ユニーク）
- `machine_no`: 機番（HMX7-CN2等）
- `model`: 機種（NEX140Ⅲ = シリーズ + トン数 + 世代）
- `spec_code`: 仕様コード（24AK）
- `full_model_name`: model + "-" + spec_code（NEX140Ⅲ-24AK）
- `work_category_id`: 作業区分（盤配/線加工）
- `delivery_destination_id`: 納入先
- `progress_id`: 進捗状態
- `planned_hours`: 予定工数（時間単位）
- `reference_code`: 参考製番
- `circuit_diagram_no`: 回路図番
- `delay_reason`: 係り超過理由

**機種名の構造**:
- **model**: シリーズ + トン数 + 世代（例: NEX140Ⅲ）
- **spec_code**: 仕様コード（例: 24AK）
- **full_model_name**: model + "-" + spec_code（例: NEX140Ⅲ-24AK）

---

### 3. work_logs（工数入力）

スプレッドシート風グリッドUI対応、15分刻み。

```sql
CREATE TABLE work_logs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id UUID REFERENCES projects(id) ON DELETE CASCADE NOT NULL,
  user_id UUID REFERENCES users(id) ON DELETE CASCADE NOT NULL,
  work_date DATE NOT NULL,
  duration_minutes INTEGER NOT NULL,
  start_time TIME,
  end_time TIME,
  work_content TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX idx_work_logs_project ON work_logs(project_id);
CREATE INDEX idx_work_logs_user ON work_logs(user_id);
CREATE INDEX idx_work_logs_date ON work_logs(work_date);
```

**フィールド説明**:
- `duration_minutes`: 作業時間（分）、15分単位（15, 30, 45, 60, 75...480）
- `start_time`, `end_time`: 開始・終了時刻（オプション）
- `work_content`: 作業内容（オプション）

**API仕様**:
- グリッドAPI: `GET /api/worklogs/grid?month=YYYY-MM`（月全体）
- 差分更新: `PUT /api/worklogs/grid`（変更行のみ）

---

### 4. materials（資料管理）

4段階スコープ（machine/model/tonnage/series）で資料を共有。

```sql
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
```

**スコープ階層**:
1. `machine`: 特定機番専用（例: HMX7-CN2専用）
2. `model`: 特定機種専用（例: NEX140Ⅲ-24AK専用）
3. `tonnage`: トン数共通（例: 140トン全機種）
4. `series`: シリーズ共通（例: NEXシリーズ全体）

**ファイルストレージ**:
- バケット名: `materials`
- 本番環境: Supabase Storage
- 開発環境: MinIO (Docker Compose)

**検索ロジック**:
```
機番から上位スコープへ展開:
HMX7-CN2 → NEX140Ⅲ-24AK → 140トン → NEXシリーズ

検索順序（狭い→広い）:
1. scope=machine AND machine_no='HMX7-CN2'
2. scope=model AND model='NEX140Ⅲ-24AK'
3. scope=tonnage AND series='NEX' AND tonnage=140
4. scope=series AND series='NEX'
```

---

### 5. invoices（請求書）

CSV出力用、月締め請求書。

```sql
CREATE TABLE invoices (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  invoice_number VARCHAR(50) UNIQUE NOT NULL,
  issue_date DATE NOT NULL,
  total_amount DECIMAL(12,2) DEFAULT 0.00 NOT NULL,
  status VARCHAR(50) DEFAULT 'draft' NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE UNIQUE INDEX idx_invoices_number ON invoices(invoice_number);
CREATE INDEX idx_invoices_status ON invoices(status);
```

**status値**:
- `draft`: 下書き（編集可能）
- `sent`: 送信済み（確定）
- `paid`: 入金済み

---

### 6. invoice_items（請求書明細）

CSV出力形式対応。

```sql
CREATE TABLE invoice_items (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  invoice_id UUID REFERENCES invoices(id) ON DELETE CASCADE NOT NULL,
  management_no VARCHAR(50) NOT NULL,
  machine_no VARCHAR(100) NOT NULL,
  actual_hours DECIMAL(10,2) NOT NULL,
  sort_order INTEGER DEFAULT 0 NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX idx_invoice_items_invoice ON invoice_items(invoice_id);
CREATE INDEX idx_invoice_items_sort ON invoice_items(sort_order);
```

**CSV出力形式**:
```csv
管理No,委託業務内容,実工数
E25A001,HMX7-CN2,5.75H
E25A002,STX10S2VS1,3.25H
```

**フィールド対応**:
- 管理No → `management_no`
- 委託業務内容 → `machine_no`
- 実工数 → `actual_hours` + "H"（例: 5.75H）

---

### 7. master_work_category（作業区分マスタ）

```sql
CREATE TABLE master_work_category (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(100) NOT NULL,
  sort_order INTEGER DEFAULT 0 NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX idx_master_work_category_sort ON master_work_category(sort_order);

-- 初期データ
INSERT INTO master_work_category (name, sort_order) VALUES
  ('盤配', 1),
  ('線加工', 2);
```

---

### 8. master_kishyu（機種マスタ）

```sql
CREATE TABLE master_kishyu (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  series VARCHAR(50) NOT NULL,
  tonnage INTEGER,
  generation VARCHAR(20),
  model_name VARCHAR(100) NOT NULL,
  is_active BOOLEAN DEFAULT true NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX idx_master_kishyu_series_tonnage ON master_kishyu(series, tonnage);
CREATE INDEX idx_master_kishyu_model_name ON master_kishyu(model_name);
```

**注意**: 機種 = シリーズ + トン数 + 世代（例: NEX140Ⅲ）。仕様コード（-24AK）は含まない。

---

### 9. master_nounyusaki（納入先マスタ）

```sql
CREATE TABLE master_nounyusaki (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(200) NOT NULL,
  code VARCHAR(50),
  sort_order INTEGER DEFAULT 0 NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX idx_master_nounyusaki_sort ON master_nounyusaki(sort_order);
```

---

### 10. master_shinchoku（進捗マスタ）

```sql
CREATE TABLE master_shinchoku (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(100) NOT NULL,
  sort_order INTEGER DEFAULT 0 NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX idx_master_shinchoku_sort ON master_shinchoku(sort_order);
```

**想定値例**: 受注済み、作図中、完成、出荷済み

---

### 11. master_chuiten_category（注意点カテゴリマスタ）

```sql
CREATE TABLE master_chuiten_category (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(100) NOT NULL,
  sort_order INTEGER DEFAULT 0 NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX idx_master_chuiten_category_sort ON master_chuiten_category(sort_order);

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
  ('端子台', 9);
```

---

### 12. master_chuiten（注意点マスタ）

```sql
CREATE TABLE master_chuiten (
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

CREATE INDEX idx_master_chuiten_category ON master_chuiten(category_id);
CREATE INDEX idx_master_chuiten_target_series ON master_chuiten(target_series);
```

**設計思想**: チェックリストではなく注意点リスト。マスター化可能な柔軟な設計。

---

## マイグレーション順序

依存関係を考慮した正しいマイグレーション順序:

```
1. users
2. master_work_category, master_kishyu, master_nounyusaki, master_shinchoku
3. master_chuiten_category
4. master_chuiten
5. projects
6. work_logs
7. materials
8. invoices
9. invoice_items
```

---

## パフォーマンス最適化

### インデックス設計

**検索頻度が高いカラム**:
- `projects.management_no` (UNIQUE)
- `projects.assignee_id`, `progress_id`, `deadline`
- `work_logs.project_id`, `user_id`, `work_date`
- `materials.scope`, `series`, `tonnage`
- `invoices.invoice_number` (UNIQUE)

**外部キー自動インデックス**:
- PostgreSQLでは外部キーに自動的にインデックスは作成されないため、明示的に作成

### クエリ最適化

**N+1問題の回避**:
```python
# 悪い例（N+1）
projects = db.table("projects").select("*").execute()
for project in projects.data:
    user = db.table("users").select("*").eq("id", project["assignee_id"]).single().execute()

# 良い例（JOIN）
projects = db.table("projects").select("""
    *,
    users:assignee_id(username),
    master_work_category:work_category_id(name),
    master_shinchoku:progress_id(name)
""").execute()
```

---

## データ整合性

### 外部キー制約

**ON DELETE動作**:
- `projects` → `users`: `ON DELETE SET NULL`（担当者削除時、案件は残す）
- `work_logs` → `projects`: `ON DELETE CASCADE`（案件削除時、工数も削除）
- `invoice_items` → `invoices`: `ON DELETE CASCADE`（請求書削除時、明細も削除）

### NOT NULL制約

**必須フィールド**:
- `projects.management_no`, `machine_no`, `model`
- `work_logs.project_id`, `user_id`, `work_date`, `duration_minutes`
- `materials.title`, `scope`, `series`, `file_path`

### UNIQUE制約

**一意性保証**:
- `users.email`
- `projects.management_no`
- `invoices.invoice_number`

---

## 関連ドキュメント

- API仕様: `.serena/memories/api_specifications.md`
- 実装状況: `.serena/memories/implementation_status.md`
- 要件定義: `docs/requirements-definition.md`（人間用簡潔版）
