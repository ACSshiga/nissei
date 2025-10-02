# API仕様書

**最終更新**: 2025-10-02
**バージョン**: v3.0

## ベースURL

```
開発環境: http://localhost:8000
本番環境: TBD (Supabase連携)
```

## 認証

すべてのAPI（ログイン・登録を除く）はJWTトークン認証が必要。

### リクエストヘッダー

```
Authorization: Bearer <access_token>
Content-Type: application/json
```

---

## エンドポイント一覧

### 認証 (Auth)

| Method | Path | 説明 |
|--------|------|------|
| POST | /api/auth/register | ユーザー登録 |
| POST | /api/auth/login | ログイン |
| GET | /api/auth/me | 現在のユーザー情報取得 |

**POST /api/auth/register**
```json
// Request
{
  "email": "user@example.com",
  "username": "user123",
  "password": "SecurePass123!"
}

// Response (201)
{
  "id": "uuid",
  "email": "user@example.com",
  "username": "user123",
  "created_at": "2025-01-01T00:00:00Z"
}
```

**POST /api/auth/login**
```json
// Request
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}

// Response (200)
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer",
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "username": "user123",
    "is_admin": false
  }
}
```

---

### 案件管理 (Projects)

| Method | Path | 説明 |
|--------|------|------|
| GET | /api/projects | 案件一覧取得（検索・フィルタ対応） |
| POST | /api/projects | 案件作成 |
| GET | /api/projects/{id} | 案件詳細取得 |
| PATCH | /api/projects/{id} | 案件更新 |
| DELETE | /api/projects/{id} | 案件削除 |
| GET | /api/projects/my | 自分の担当案件一覧 |

**GET /api/projects クエリパラメータ**
- `page`: ページ番号（デフォルト: 1）
- `per_page`: 1ページあたりの件数（デフォルト: 20）
- `management_no`: 管理No（部分一致）
- `machine_no`: 機番（部分一致）
- `model`: 機種（部分一致）
- `assignee_id`: 担当者ID（複数可: カンマ区切り）
- `progress_id`: 進捗ID（複数可: カンマ区切り）
- `work_category_id`: 作業区分ID（複数可: カンマ区切り）
- `started_at_from`, `started_at_to`: 仕掛日範囲
- `completed_at_from`, `completed_at_to`: 完了日範囲
- `deadline_from`, `deadline_to`: 作図期限範囲
- `sort_by`: ソート項目（management_no/deadline/started_at/completed_at）
- `sort_order`: ソート順（asc/desc）

**POST /api/projects**
```json
// Request
{
  "management_no": "E252019",
  "machine_no": "HMX7-CN2",
  "model": "NEX140Ⅲ",
  "spec_code": "24AK",
  "work_category_id": "uuid",
  "delivery_destination_id": "uuid",
  "assignee_id": "uuid",
  "progress_id": "uuid",
  "planned_hours": 40.0,
  "deadline": "2025-03-31",
  "reference_code": "REF001",
  "circuit_diagram_no": "CD001",
  "notes": "備考"
}

// Response (201)
{
  "id": "uuid",
  "management_no": "E252019",
  "machine_no": "HMX7-CN2",
  "model": "NEX140Ⅲ",
  "spec_code": "24AK",
  "full_model_name": "NEX140Ⅲ-24AK",
  // ... 全フィールド
}
```

---

### 工数入力 (Work Logs)

| Method | Path | 説明 |
|--------|------|------|
| GET | /api/worklogs | 工数一覧取得 |
| POST | /api/worklogs | 工数作成 |
| GET | /api/worklogs/{id} | 工数詳細取得 |
| PUT | /api/worklogs/{id} | 工数更新 |
| DELETE | /api/worklogs/{id} | 工数削除 |
| **GET** | **/api/worklogs/grid** | **月グリッドデータ取得** |
| **PUT** | **/api/worklogs/grid** | **差分パッチ更新** |

**GET /api/worklogs/grid?month=YYYY-MM**

スプレッドシート風UI用、月全体のグリッドデータを取得。

```json
// Response (200)
{
  "month": "2025-01",
  "projects": [
    {
      "id": "uuid",
      "management_no": "E252019",
      "machine_no": "HMX7-CN2",
      "model": "NEX140Ⅲ-24AK"
    }
  ],
  "work_logs": [
    {
      "id": "uuid",
      "project_id": "uuid",
      "user_id": "uuid",
      "work_date": "2025-01-15",
      "duration_minutes": 480,
      "start_time": "09:00",
      "end_time": "17:00",
      "work_content": "配線作業"
    }
  ]
}
```

**PUT /api/worklogs/grid**

複数行を一度に更新（差分のみ）。

```json
// Request
{
  "month": "2025-01",
  "updates": [
    {
      "id": "uuid",  // 既存IDがあれば更新
      "project_id": "uuid",
      "work_date": "2025-01-15",
      "duration_minutes": 480,
      "start_time": "09:00",
      "end_time": "17:00",
      "work_content": "配線作業"
    },
    {
      // IDなし → 新規作成
      "project_id": "uuid",
      "work_date": "2025-01-16",
      "duration_minutes": 240
    }
  ],
  "deletes": ["uuid1", "uuid2"]  // 削除対象ID
}

// Response (200)
{
  "created": 1,
  "updated": 1,
  "deleted": 2
}
```

---

### 請求書 (Invoices)

| Method | Path | 説明 |
|--------|------|------|
| **GET** | **/api/invoices/preview?year=YYYY&month=MM** | **請求プレビュー** |
| **POST** | **/api/invoices/close?year=YYYY&month=MM** | **請求締め確定（管理者のみ）** |
| **GET** | **/api/invoices/export?year=YYYY&month=MM** | **CSV出力** |
| **GET** | **/api/invoices** | **請求書一覧取得** |
| **DELETE** | **/api/invoices/{invoice_id}** | **請求書削除（管理者のみ）** |

**年月管理**: `year`と`month`パラメータで管理（UNIQUE制約: `(year, month)`）
**ステータス**: `draft` | `closed`

**GET /api/invoices/preview?year=YYYY&month=MM**

指定月の請求書プレビュー（work_logsから実工数を自動集計）。

```json
// Response (200)
{
  "id": "uuid",  // 既存の請求書があればそのID、なければダミー
  "year": 2025,
  "month": 1,
  "status": "draft",
  "closed_at": null,
  "closed_by": null,
  "created_at": "2025-01-01T00:00:00Z",
  "updated_at": "2025-01-01T00:00:00Z",
  "items": [
    {
      "id": "uuid",
      "invoice_id": "uuid",
      "project_id": "uuid",
      "management_no": "E252019",
      "work_content": "HMX7-CN2",
      "total_hours": 5.75,
      "created_at": "2025-01-01T00:00:00Z"
    }
  ]
}
```

**POST /api/invoices/close?year=YYYY&month=MM**

請求書を確定（管理者のみ）。work_logsから工数集計し、invoices + invoice_items作成。

```json
// Response (200)
{
  "id": "uuid",
  "year": 2025,
  "month": 1,
  "status": "closed",
  "closed_at": "2025-02-01T00:00:00Z",
  "closed_by": "uuid",
  "created_at": "2025-01-01T00:00:00Z",
  "updated_at": "2025-02-01T00:00:00Z"
}
```

**GET /api/invoices/export?year=YYYY&month=MM**

CSV形式でダウンロード（BOM付きUTF-8）。

```csv
管理No,委託業務内容,実工数
E252019,HMX7-CN2,5.75
E252020,STX10S2VS1,3.25
```

**Content-Type**: `text/csv; charset=utf-8-sig`
**Content-Disposition**: `attachment; filename=invoice_YYYY-MM.csv`

**GET /api/invoices**

請求書一覧を取得（年・月の降順）。

```json
// Response (200)
[
  {
    "id": "uuid",
    "year": 2025,
    "month": 1,
    "status": "closed",
    "closed_at": "2025-02-01T00:00:00Z",
    "closed_by": "uuid",
    "created_at": "2025-01-01T00:00:00Z",
    "updated_at": "2025-02-01T00:00:00Z"
  }
]
```

**DELETE /api/invoices/{invoice_id}**

請求書と関連する明細をCASCADE削除（管理者のみ）。

```json
// Response (200)
{
  "message": "請求書を削除しました"
}
```

---

### 資料管理 (Materials)

| Method | Path | 説明 |
|--------|------|------|
| GET | /api/materials?scope={scope}&key={value} | 資料一覧取得 |
| POST | /api/materials | 資料追加（ファイルアップロード） |
| PUT | /api/materials/{id} | 資料メタデータ更新 |
| DELETE | /api/materials/{id} | 資料削除 |

**GET /api/materials クエリパラメータ**
- `scope`: machine | model | tonnage | series
- `machine_no`: 機番（scope=machineの場合）
- `model`: 機種（scope=modelの場合）
- `series`: シリーズ（scope=tonnage or series）
- `tonnage`: トン数（scope=tonnageの場合）

**検索ロジック**:
```
機番 HMX7-CN2 → NEX140Ⅲ-24AK → 140トン → NEXシリーズ

検索順序（狭い→広い）:
1. scope=machine AND machine_no='HMX7-CN2'
2. scope=model AND model='NEX140Ⅲ-24AK'
3. scope=tonnage AND series='NEX' AND tonnage=140
4. scope=series AND series='NEX'
```

**POST /api/materials**

ファイルアップロード（multipart/form-data）。

```
Content-Type: multipart/form-data

Fields:
- file: File (required)
- title: string (required)
- scope: string (required)
- series: string (required)
- tonnage: integer (optional)
- machine_no: string (optional)
- model: string (optional)
```

**Response (201)**
```json
{
  "id": "uuid",
  "title": "配線図_NEX140Ⅲ",
  "scope": "model",
  "model": "NEX140Ⅲ-24AK",
  "series": "NEX",
  "tonnage": 140,
  "file_path": "materials/uuid/filename.pdf",
  "file_size": 1048576,
  "uploaded_by": "uuid",
  "created_at": "2025-01-01T00:00:00Z"
}
```

---

### 注意点管理 (Chuiten)

#### 注意点カテゴリ

| Method | Path | 説明 |
|--------|------|------|
| **GET** | **/api/chuiten/categories** | カテゴリ一覧取得 |
| **POST** | **/api/chuiten/categories** | カテゴリ追加（管理者のみ） |
| **DELETE** | **/api/chuiten/categories/{id}** | カテゴリ削除（管理者のみ） |

**GET /api/chuiten/categories**

```json
// Response (200)
[
  {
    "id": "uuid",
    "name": "A板",
    "sort_order": 1
  }
]
```

**POST /api/chuiten/categories**

```json
// Request
{
  "name": "A板",
  "sort_order": 1
}

// Response (201)
{
  "id": "uuid",
  "name": "A板",
  "sort_order": 1
}
```

**DELETE /api/chuiten/categories/{id}**

使用中のカテゴリは削除不可。

```json
// Response (200)
{
  "message": "カテゴリを削除しました"
}

// Response (400 - 使用中)
{
  "detail": "このカテゴリは使用中のため削除できません"
}
```

#### 注意点マスタ

| Method | Path | 説明 |
|--------|------|------|
| **GET** | **/api/chuiten** | 注意点一覧取得（カテゴリ・シリーズ別フィルタ対応） |
| **POST** | **/api/chuiten** | 注意点追加（管理者のみ） |
| **GET** | **/api/chuiten/{id}** | 注意点詳細取得 |
| **PATCH** | **/api/chuiten/{id}** | 注意点更新（管理者のみ） |
| **DELETE** | **/api/chuiten/{id}** | 注意点削除（管理者のみ） |

**GET /api/chuiten クエリパラメータ**
- `category_id`: カテゴリID（UUID）
- `target_series`: 対象シリーズ（NEX, HMX等）

**GET /api/chuiten**

```json
// Response (200)
[
  {
    "id": "uuid",
    "seq_no": 1,
    "target_series": "NEX",
    "target_model_pattern": "NEX.*140.*",
    "category_id": "uuid",
    "category_name": "A板",
    "note": "端子台配置に注意",
    "author": "田中",
    "remarks": "2024年改訂"
  }
]
```

**POST /api/chuiten**

```json
// Request
{
  "seq_no": 1,
  "target_series": "NEX",
  "target_model_pattern": "NEX.*140.*",
  "category_id": "uuid",
  "note": "端子台配置に注意",
  "author": "田中",
  "remarks": "2024年改訂"
}

// Response (201)
{
  "id": "uuid",
  "seq_no": 1,
  "target_series": "NEX",
  "target_model_pattern": "NEX.*140.*",
  "category_id": "uuid",
  "note": "端子台配置に注意",
  "author": "田中",
  "remarks": "2024年改訂"
}
```

**PATCH /api/chuiten/{id}**

部分更新対応。

```json
// Request
{
  "seq_no": 2,
  "note": "端子台配置に注意（更新版）"
}

// Response (200)
{
  "id": "uuid",
  "seq_no": 2,
  "target_series": "NEX",
  "target_model_pattern": "NEX.*140.*",
  "category_id": "uuid",
  "note": "端子台配置に注意（更新版）",
  "author": "田中",
  "remarks": "2024年改訂"
}
```

#### 案件別注意点取得

| Method | Path | 説明 |
|--------|------|------|
| **GET** | **/api/chuiten/by-project/{project_id}** | 案件の機種に該当する注意点一覧取得 |

**GET /api/chuiten/by-project/{project_id}**

案件の機種（model）から自動的にシリーズを抽出し、該当する注意点をフィルタ。

```json
// Response (200)
[
  {
    "id": "uuid",
    "seq_no": 1,
    "target_series": "NEX",
    "target_model_pattern": "NEX.*140.*",
    "category_id": "uuid",
    "category_name": "A板",
    "note": "端子台配置に注意",
    "author": "田中",
    "remarks": "2024年改訂"
  }
]
```

---

### マスタ管理 (Masters)

各マスタに対して同じCRUD操作が可能。

| エンドポイント | マスタ名 |
|-------------|---------|
| /api/masters/work-category | 作業区分 |
| /api/masters/kishyu | 機種 |
| /api/masters/nounyusaki | 納入先 |
| /api/masters/shinchoku | 進捗 |
| /api/masters/chuiten-category | 注意点カテゴリ |

**共通操作**:
```
GET    /api/masters/{type}        一覧取得
POST   /api/masters/{type}        新規作成
PUT    /api/masters/{type}/{id}   更新
DELETE /api/masters/{type}/{id}   削除
```

**作業区分マスタ (work-category)**
```json
{
  "id": "uuid",
  "name": "盤配",
  "sort_order": 1
}
```

**機種マスタ (kishyu)**
```json
{
  "id": "uuid",
  "series": "NEX",
  "tonnage": 140,
  "generation": "Ⅲ",
  "model_name": "NEX140Ⅲ",
  "is_active": true
}
```

**納入先マスタ (nounyusaki)**
```json
{
  "id": "uuid",
  "name": "株式会社ABC",
  "code": "ABC001",
  "sort_order": 1
}
```

**進捗マスタ (shinchoku)**
```json
{
  "id": "uuid",
  "name": "作図中",
  "sort_order": 2
}
```

**注意点カテゴリマスタ (chuiten-category)**
```json
{
  "id": "uuid",
  "name": "A板",
  "sort_order": 1
}
```

---

### 管理者機能 (Admin)

| Method | Path | 説明 |
|--------|------|------|
| GET | /api/admin/users | 全ユーザー一覧 |
| DELETE | /api/admin/users/{id} | ユーザー削除 |
| PATCH | /api/admin/users/{id}/activate | ユーザー有効化 |
| PATCH | /api/admin/users/{id}/deactivate | ユーザー無効化 |

**認可**: `is_admin=true` のユーザーのみアクセス可能

---

## エラーレスポンス

### 共通エラー形式

```json
{
  "detail": "エラーメッセージ"
}
```

### HTTPステータスコード

| Code | 意味 | 例 |
|------|-----|---|
| 200 | OK | 正常取得 |
| 201 | Created | 作成成功 |
| 400 | Bad Request | バリデーションエラー |
| 401 | Unauthorized | 認証エラー |
| 403 | Forbidden | 権限エラー |
| 404 | Not Found | リソースが存在しない |
| 409 | Conflict | 重複エラー |
| 422 | Unprocessable Entity | リクエスト形式エラー |
| 500 | Internal Server Error | サーバーエラー |

---

## バリデーション

### 工数入力
- `duration_minutes`: 15の倍数（15, 30, 45, 60...480）
- `work_date`: 未来日不可

### 案件管理
- `management_no`: ユニーク制約
- `planned_hours`: 0以上

### ファイルアップロード
- 最大ファイルサイズ: 10MB
- 許可形式: PDF, PNG, JPG, XLSX, DOCX

---

## ページネーション

**リクエスト**:
```
GET /api/projects?page=2&per_page=20
```

**レスポンス**:
```json
{
  "items": [...],
  "total": 150,
  "page": 2,
  "per_page": 20,
  "pages": 8
}
```

---

## 関連ドキュメント

- データベース仕様: `.serena/memories/database_specifications.md`
- 実装状況: `.serena/memories/implementation_status.md`
