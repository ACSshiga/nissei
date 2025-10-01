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
  "refresh_token": "eyJhbGc...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

#### POST /api/auth/refresh
トークンリフレッシュ

**リクエスト**
```json
{
  "refresh_token": "eyJhbGc..."
}
```

**レスポンス (200 OK)**
```json
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

#### POST /api/auth/logout
ログアウト

**レスポンス (200 OK)**
```json
{
  "message": "Successfully logged out"
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

### 作業履歴 (Work Logs)

#### GET /api/projects/{project_id}/work-logs
作業履歴一覧取得

**レスポンス (200 OK)**
```json
{
  "items": [
    {
      "id": "uuid",
      "project_id": "uuid",
      "date": "2025-01-01",
      "description": "作業内容",
      "hours": 8.0,
      "created_at": "2025-01-01T00:00:00Z"
    }
  ],
  "total": 50,
  "page": 1,
  "pages": 3
}
```

#### POST /api/projects/{project_id}/work-logs
作業履歴作成

**リクエスト**
```json
{
  "date": "2025-01-01",
  "description": "作業内容の説明",
  "hours": 8.0
}
```

**レスポンス (201 Created)**
```json
{
  "id": "uuid",
  "project_id": "uuid",
  "date": "2025-01-01",
  "description": "作業内容の説明",
  "hours": 8.0,
  "created_at": "2025-01-01T00:00:00Z"
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
