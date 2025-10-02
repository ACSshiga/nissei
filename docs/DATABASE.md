# データベース設計

## データベース構成

- **プラットフォーム**: Supabase (PostgreSQL)
- **プロジェクトID**: wwyrthkizkcgndyorcww
- **バージョン**: PostgreSQL 15

## ER図

```
users
├── id (PK)
├── email
├── username
├── password_hash
├── is_active
└── is_admin

projects
├── id (PK)
├── user_id (FK → users.id)
├── name
├── description
├── status
├── start_date
├── end_date
├── estimated_hours
├── actual_hours
└── management_no

work_logs
├── id (PK)
├── project_id (FK → projects.id)
├── user_id (FK → users.id)
├── work_date
├── duration_minutes
├── start_time
├── end_time
└── work_content

materials
├── id (PK)
├── project_id (FK → projects.id)
├── category_id (FK → material_categories.id)
├── name
├── quantity
└── unit_price

invoices
├── id (PK)
├── project_id (FK → projects.id)
├── invoice_number
├── issue_date
├── due_date
├── total_amount
└── status

checklists
├── id (PK)
├── project_id (FK → projects.id)
├── title
└── is_completed

material_categories (マスタ)
├── id (PK)
├── name
├── code
└── sort_order

work_types (マスタ)
├── id (PK)
├── name
├── code
└── sort_order
```

## テーブル定義

### users（ユーザー）

| カラム名 | 型 | NULL | デフォルト | 説明 |
|---------|---|------|----------|------|
| id | UUID | NO | gen_random_uuid() | 主キー |
| email | VARCHAR(255) | NO | - | メールアドレス（ユニーク） |
| username | VARCHAR(100) | NO | - | ユーザー名 |
| password_hash | VARCHAR(255) | NO | - | ハッシュ化パスワード |
| is_active | BOOLEAN | NO | true | アクティブフラグ |
| is_admin | BOOLEAN | NO | false | 管理者フラグ |
| created_at | TIMESTAMP | NO | CURRENT_TIMESTAMP | 作成日時 |
| updated_at | TIMESTAMP | NO | CURRENT_TIMESTAMP | 更新日時 |

**インデックス**
- PRIMARY KEY (id)
- UNIQUE INDEX (email)

---

### projects（プロジェクト）

| カラム名 | 型 | NULL | デフォルト | 説明 |
|---------|---|------|----------|------|
| id | UUID | NO | gen_random_uuid() | 主キー |
| user_id | UUID | NO | - | ユーザーID（外部キー） |
| name | VARCHAR(200) | NO | - | プロジェクト名 |
| description | TEXT | YES | NULL | 説明 |
| status | VARCHAR(50) | NO | 'planning' | ステータス（planning/in_progress/completed） |
| start_date | DATE | YES | NULL | 開始日 |
| end_date | DATE | YES | NULL | 終了日 |
| estimated_hours | DECIMAL(10,2) | NO | 0.00 | 予定工数（時間） |
| actual_hours | DECIMAL(10,2) | NO | 0.00 | 実績工数（時間） |
| management_no | VARCHAR(50) | YES | NULL | 管理番号（ユニーク） |
| created_at | TIMESTAMP | NO | CURRENT_TIMESTAMP | 作成日時 |
| updated_at | TIMESTAMP | NO | CURRENT_TIMESTAMP | 更新日時 |

**インデックス**
- PRIMARY KEY (id)
- INDEX (user_id)
- INDEX (status)
- INDEX (start_date, end_date)

**外部キー**
- user_id → users(id) ON DELETE CASCADE

---

### work_logs（作業履歴）

| カラム名 | 型 | NULL | デフォルト | 説明 |
|---------|---|------|----------|------|
| id | UUID | NO | gen_random_uuid() | 主キー |
| project_id | UUID | NO | - | プロジェクトID（外部キー） |
| user_id | UUID | NO | - | ユーザーID（外部キー） |
| work_date | DATE | NO | - | 作業日 |
| duration_minutes | INTEGER | NO | - | 作業時間（分）※15分単位 |
| start_time | TIME | YES | NULL | 作業開始時刻 |
| end_time | TIME | YES | NULL | 作業終了時刻 |
| work_content | TEXT | YES | NULL | 作業内容 |
| created_at | TIMESTAMP | NO | CURRENT_TIMESTAMP | 作成日時 |
| updated_at | TIMESTAMP | NO | CURRENT_TIMESTAMP | 更新日時 |

**インデックス**
- PRIMARY KEY (id)
- INDEX (project_id)
- INDEX (user_id)
- INDEX (work_date)

**外部キー**
- project_id → projects(id) ON DELETE CASCADE
- user_id → users(id) ON DELETE CASCADE

---

### materials（資材）

| カラム名 | 型 | NULL | デフォルト | 説明 |
|---------|---|------|----------|------|
| id | UUID | NO | gen_random_uuid() | 主キー |
| project_id | UUID | NO | - | プロジェクトID（外部キー） |
| category_id | UUID | YES | NULL | カテゴリID（外部キー） |
| name | VARCHAR(200) | NO | - | 資材名 |
| quantity | INTEGER | NO | 0 | 数量 |
| unit_price | DECIMAL(10,2) | NO | 0.00 | 単価 |
| created_at | TIMESTAMP | NO | CURRENT_TIMESTAMP | 作成日時 |
| updated_at | TIMESTAMP | NO | CURRENT_TIMESTAMP | 更新日時 |

**インデックス**
- PRIMARY KEY (id)
- INDEX (project_id)
- INDEX (category_id)

**外部キー**
- project_id → projects(id) ON DELETE CASCADE
- category_id → material_categories(id) ON DELETE SET NULL

---

### invoices（請求書）

| カラム名 | 型 | NULL | デフォルト | 説明 |
|---------|---|------|----------|------|
| id | UUID | NO | gen_random_uuid() | 主キー |
| project_id | UUID | NO | - | プロジェクトID（外部キー） |
| invoice_number | VARCHAR(50) | NO | - | 請求書番号（ユニーク） |
| issue_date | DATE | NO | - | 発行日 |
| due_date | DATE | YES | NULL | 支払期限 |
| total_amount | DECIMAL(12,2) | NO | 0.00 | 合計金額 |
| status | VARCHAR(50) | NO | 'draft' | ステータス（draft/sent/paid） |
| created_at | TIMESTAMP | NO | CURRENT_TIMESTAMP | 作成日時 |
| updated_at | TIMESTAMP | NO | CURRENT_TIMESTAMP | 更新日時 |

**インデックス**
- PRIMARY KEY (id)
- UNIQUE INDEX (invoice_number)
- INDEX (project_id)
- INDEX (status)

**外部キー**
- project_id → projects(id) ON DELETE CASCADE

---

### checklists（チェックリスト）

| カラム名 | 型 | NULL | デフォルト | 説明 |
|---------|---|------|----------|------|
| id | UUID | NO | gen_random_uuid() | 主キー |
| project_id | UUID | NO | - | プロジェクトID（外部キー） |
| title | VARCHAR(200) | NO | - | チェック項目 |
| is_completed | BOOLEAN | NO | false | 完了フラグ |
| sort_order | INTEGER | NO | 0 | 表示順序 |
| created_at | TIMESTAMP | NO | CURRENT_TIMESTAMP | 作成日時 |
| updated_at | TIMESTAMP | NO | CURRENT_TIMESTAMP | 更新日時 |

**インデックス**
- PRIMARY KEY (id)
- INDEX (project_id)
- INDEX (sort_order)

**外部キー**
- project_id → projects(id) ON DELETE CASCADE

---

### material_categories（資材カテゴリマスタ）

| カラム名 | 型 | NULL | デフォルト | 説明 |
|---------|---|------|----------|------|
| id | UUID | NO | gen_random_uuid() | 主キー |
| name | VARCHAR(100) | NO | - | カテゴリ名 |
| code | VARCHAR(50) | NO | - | コード（ユニーク） |
| sort_order | INTEGER | NO | 0 | 表示順序 |
| created_at | TIMESTAMP | NO | CURRENT_TIMESTAMP | 作成日時 |
| updated_at | TIMESTAMP | NO | CURRENT_TIMESTAMP | 更新日時 |

**インデックス**
- PRIMARY KEY (id)
- UNIQUE INDEX (code)
- INDEX (sort_order)

---

### work_types（作業種別マスタ）

| カラム名 | 型 | NULL | デフォルト | 説明 |
|---------|---|------|----------|------|
| id | UUID | NO | gen_random_uuid() | 主キー |
| name | VARCHAR(100) | NO | - | 作業種別名 |
| code | VARCHAR(50) | NO | - | コード（ユニーク） |
| sort_order | INTEGER | NO | 0 | 表示順序 |
| created_at | TIMESTAMP | NO | CURRENT_TIMESTAMP | 作成日時 |
| updated_at | TIMESTAMP | NO | CURRENT_TIMESTAMP | 更新日時 |

**インデックス**
- PRIMARY KEY (id)
- UNIQUE INDEX (code)
- INDEX (sort_order)

---

## マイグレーション

### 初期セットアップ

```bash
cd backend
alembic upgrade head
```

### 新しいマイグレーション作成

```bash
alembic revision --autogenerate -m "マイグレーション名"
```

### マイグレーション適用

```bash
alembic upgrade head
```

### ロールバック

```bash
alembic downgrade -1  # 1つ前に戻す
alembic downgrade base  # すべてロールバック
```

## データベース設計の原則

### 命名規則
- テーブル名: 複数形、`snake_case`
- カラム名: `snake_case`
- 主キー: `id`（UUID型）
- 外部キー: `<テーブル名単数形>_id`
- タイムスタンプ: `created_at`, `updated_at`

### パフォーマンス最適化
- 頻繁に検索されるカラムにINDEX作成
- 外部キーに自動的にINDEX作成
- N+1クエリを避けるためにEager Loadingを使用

### データ整合性
- 外部キー制約を設定
- NOT NULL制約を適切に使用
- UNIQUE制約で一意性を保証

## 関連ドキュメント

- [API仕様](./API.md)
- [環境構築](./SETUP.md)
- [命名規則](../ai-rules/NAMING_CONVENTIONS.md)
