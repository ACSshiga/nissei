# API仕様書

## ベースURL

```
開発環境: http://localhost:8000
本番環境: TBD
```

## 認証

すべてのAPI（ログイン・登録を除く）はJWTトークン認証が必要です。

### リクエストヘッダー

```
Authorization: Bearer <access_token>
Content-Type: application/json
```

## エンドポイント一覧

### 認証 (Auth)

#### POST /api/auth/register
ユーザー登録

**リクエスト**
```json
{
  "email": "user@example.com",
  "username": "user123",
  "password": "SecurePass123!"
}
```

**レスポンス (201 Created)**
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "username": "user123",
  "created_at": "2025-01-01T00:00:00Z"
}
```

#### POST /api/auth/login
ログイン

**リクエスト**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```

**レスポンス (200 OK)**
```json
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer"
}
```

---

### ユーザー (Users)

#### GET /api/users/me
現在のユーザー情報取得

**レスポンス (200 OK)**
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "username": "user123",
  "created_at": "2025-01-01T00:00:00Z",
  "updated_at": "2025-01-01T00:00:00Z"
}
```

#### PATCH /api/users/me
現在のユーザー情報更新

**リクエスト**
```json
{
  "username": "newusername",
  "email": "newemail@example.com"
}
```

**レスポンス (200 OK)**
```json
{
  "id": "uuid",
  "email": "newemail@example.com",
  "username": "newusername",
  "updated_at": "2025-01-02T00:00:00Z"
}
```

---

### プロジェクト (Projects)

#### GET /api/projects
プロジェクト一覧取得

**クエリパラメータ**
- `page`: ページ番号（デフォルト: 1）
- `limit`: 1ページあたりの件数（デフォルト: 20）
- `status`: ステータスフィルター（planning/in_progress/completed）

**レスポンス (200 OK)**
```json
{
  "items": [
    {
      "id": "uuid",
      "name": "プロジェクトA",
      "description": "説明",
      "status": "in_progress",
      "start_date": "2025-01-01",
      "end_date": "2025-12-31",
      "created_at": "2025-01-01T00:00:00Z"
    }
  ],
  "total": 100,
  "page": 1,
  "pages": 5
}
```

#### POST /api/projects
プロジェクト作成

**リクエスト**
```json
{
  "name": "プロジェクトA",
  "description": "プロジェクト説明",
  "start_date": "2025-01-01",
  "end_date": "2025-12-31"
}
```

**レスポンス (201 Created)**
```json
{
  "id": "uuid",
  "name": "プロジェクトA",
  "description": "プロジェクト説明",
  "status": "planning",
  "start_date": "2025-01-01",
  "end_date": "2025-12-31",
  "created_at": "2025-01-01T00:00:00Z"
}
```

#### GET /api/projects/{id}
特定プロジェクト取得

**レスポンス (200 OK)**
```json
{
  "id": "uuid",
  "name": "プロジェクトA",
  "description": "説明",
  "status": "in_progress",
  "start_date": "2025-01-01",
  "end_date": "2025-12-31",
  "created_at": "2025-01-01T00:00:00Z",
  "updated_at": "2025-01-02T00:00:00Z"
}
```

#### PATCH /api/projects/{id}
プロジェクト更新

**リクエスト**
```json
{
  "name": "更新後の名前",
  "status": "completed"
}
```

**レスポンス (200 OK)**
```json
{
  "id": "uuid",
  "name": "更新後の名前",
  "status": "completed",
  "updated_at": "2025-01-02T00:00:00Z"
}
```

#### DELETE /api/projects/{id}
プロジェクト削除

**レスポンス (204 No Content)**

---

### 工数入力 (Work Logs)

#### GET /api/worklogs
工数入力一覧取得

**クエリパラメータ**
- `page`: ページ番号（デフォルト: 1）
- `per_page`: 1ページあたりの件数（デフォルト: 20）
- `project_id`: プロジェクトIDでフィルタ
- `work_date`: 作業日でフィルタ
- `user_id`: ユーザーIDでフィルタ

**レスポンス (200 OK)**
```json
{
  "worklogs": [
    {
      "id": "uuid",
      "project_id": "uuid",
      "user_id": "uuid",
      "work_date": "2025-01-01",
      "duration_minutes": 480,
      "start_time": "09:00:00",
      "end_time": "17:00:00",
      "work_content": "作業内容",
      "created_at": "2025-01-01T00:00:00Z",
      "updated_at": "2025-01-01T00:00:00Z"
    }
  ],
  "total": 50,
  "page": 1,
  "per_page": 20
}
```

#### POST /api/worklogs
工数入力作成

**リクエスト**
```json
{
  "project_id": "uuid",
  "work_date": "2025-01-01",
  "duration_minutes": 480,
  "start_time": "09:00:00",
  "end_time": "17:00:00",
  "work_content": "作業内容の説明"
}
```

**注意**:
- `duration_minutes` は15分刻みでの入力を推奨（15, 30, 45, 60, ...）
- `start_time`, `end_time`, `work_content` はオプション（duration_minutesは必須）

**レスポンス (201 Created)**
```json
{
  "id": "uuid",
  "project_id": "uuid",
  "user_id": "uuid",
  "work_date": "2025-01-01",
  "duration_minutes": 480,
  "start_time": "09:00:00",
  "end_time": "17:00:00",
  "work_content": "作業内容の説明",
  "created_at": "2025-01-01T00:00:00Z",
  "updated_at": "2025-01-01T00:00:00Z"
}
```

#### GET /api/worklogs/{id}
特定の工数入力取得

**レスポンス (200 OK)**
```json
{
  "id": "uuid",
  "project_id": "uuid",
  "user_id": "uuid",
  "work_date": "2025-01-01",
  "duration_minutes": 480,
  "start_time": "09:00:00",
  "end_time": "17:00:00",
  "work_content": "作業内容",
  "created_at": "2025-01-01T00:00:00Z",
  "updated_at": "2025-01-01T00:00:00Z"
}
```

#### PUT /api/worklogs/{id}
工数入力更新

**リクエスト**
```json
{
  "project_id": "uuid",
  "work_date": "2025-01-02",
  "duration_minutes": 240,
  "start_time": "10:00:00",
  "end_time": "14:00:00",
  "work_content": "更新後の作業内容"
}
```

**レスポンス (200 OK)**
```json
{
  "id": "uuid",
  "project_id": "uuid",
  "user_id": "uuid",
  "work_date": "2025-01-02",
  "duration_minutes": 240,
  "start_time": "10:00:00",
  "end_time": "14:00:00",
  "work_content": "更新後の作業内容",
  "created_at": "2025-01-01T00:00:00Z",
  "updated_at": "2025-01-02T00:00:00Z"
}
```

#### DELETE /api/worklogs/{id}
工数入力削除

**レスポンス (204 No Content)**

#### GET /api/worklogs/summary/{project_id}
プロジェクト別工数サマリー取得

**レスポンス (200 OK)**
```json
{
  "project_id": "uuid",
  "management_no": "A001",
  "estimated_hours": 100.0,
  "actual_hours": 75.5,
  "by_user": [
    {
      "username": "user1",
      "total_minutes": 2400,
      "entry_count": 5
    }
  ],
  "by_date": [
    {
      "work_date": "2025-01-01",
      "total_minutes": 480,
      "entry_count": 2
    }
  ]
}
```

---

### 管理者API (Admin)

**注意**: すべての管理者APIは `is_admin=True` のユーザーのみアクセス可能

#### GET /api/admin/users
全ユーザー一覧取得

**レスポンス (200 OK)**
```json
{
  "users": [
    {
      "id": "uuid",
      "email": "user@example.com",
      "username": "user123",
      "is_active": true,
      "is_admin": false,
      "created_at": "2025-01-01T00:00:00Z"
    }
  ]
}
```

#### DELETE /api/admin/users/{user_id}
ユーザー削除

**注意**:
- 自分自身は削除不可
- 削除したユーザーのデータは保持される

**レスポンス (200 OK)**
```json
{
  "message": "ユーザー user123 を削除しました"
}
```

#### PATCH /api/admin/users/{user_id}/activate
ユーザーをアクティブ化

**レスポンス (200 OK)**
```json
{
  "message": "ユーザーをアクティブ化しました"
}
```

#### PATCH /api/admin/users/{user_id}/deactivate
ユーザーを非アクティブ化

**注意**: 自分自身は非アクティブ化不可

**レスポンス (200 OK)**
```json
{
  "message": "ユーザーを非アクティブ化しました"
}
```

---

### マスタデータ (Masters)

#### GET /api/masters/work-types
作業種別マスタ取得

**レスポンス (200 OK)**
```json
[
  {
    "id": "uuid",
    "name": "現場作業",
    "code": "field_work",
    "sort_order": 1
  }
]
```

#### GET /api/masters/material-categories
資材カテゴリマスタ取得

**レスポンス (200 OK)**
```json
[
  {
    "id": "uuid",
    "name": "電気資材",
    "code": "electrical",
    "sort_order": 1
  }
]
```

---

## エラーレスポンス

### 400 Bad Request
```json
{
  "detail": "Invalid request parameters"
}
```

### 401 Unauthorized
```json
{
  "detail": "Could not validate credentials"
}
```

### 403 Forbidden
```json
{
  "detail": "Not enough permissions"
}
```

### 404 Not Found
```json
{
  "detail": "Resource not found"
}
```

### 422 Unprocessable Entity
```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "value is not a valid email address",
      "type": "value_error.email"
    }
  ]
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```

## レート制限

現在は未実装（将来的に追加予定）

## バージョニング

現在は `/api/` プレフィックスを使用。
将来的に `/api/v1/` などのバージョニングを追加予定。

## APIドキュメント

開発環境では自動生成されたAPIドキュメントが利用可能：

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 関連ドキュメント

- [データベース設計](./DATABASE.md)
- [命名規則](../ai-rules/NAMING_CONVENTIONS.md)
