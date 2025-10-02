# API仕様

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

## エンドポイント一覧

### 認証 (Auth)

```
POST   /api/auth/register    ユーザー登録
POST   /api/auth/login       ログイン
GET    /api/auth/me          現在のユーザー情報取得
```

### 案件管理 (Projects)

```
GET    /api/projects         案件一覧取得（検索・フィルタ対応）
POST   /api/projects         案件作成
GET    /api/projects/{id}    案件詳細取得
PATCH  /api/projects/{id}    案件更新
DELETE /api/projects/{id}    案件削除
GET    /api/projects/my      自分の担当案件
```

### 工数入力 (Work Logs)

```
GET    /api/worklogs              工数一覧取得
POST   /api/worklogs              工数作成
GET    /api/worklogs/{id}         工数詳細取得
PUT    /api/worklogs/{id}         工数更新
DELETE /api/worklogs/{id}         工数削除
GET    /api/worklogs/grid         月グリッドデータ取得
PUT    /api/worklogs/grid         差分パッチ更新
```

### 請求書 (Invoices)

```
GET    /api/invoices/preview?year=YYYY&month=MM  請求プレビュー（工数自動集計）
POST   /api/invoices/close?year=YYYY&month=MM    請求締め確定（管理者のみ）
GET    /api/invoices/export?year=YYYY&month=MM   CSV出力（BOM付きUTF-8）
```

**年月管理**: `year`と`month`パラメータで管理（UNIQUEキー）
**ステータス**: `draft` | `closed`

### 資料管理 (Materials)

```
GET    /api/materials                  資料一覧取得
POST   /api/materials                  資料追加（ファイルアップロード）
PUT    /api/materials/{id}             資料更新
DELETE /api/materials/{id}             資料削除
```

**検索パラメータ**:
- `scope`: machine | model | tonnage | series
- `machine_no`: 機番
- `model`: 機種
- `series`: シリーズ
- `tonnage`: トン数

### 注意点管理 (Chuiten)

```
GET    /api/chuiten/categories           カテゴリ一覧取得
POST   /api/chuiten/categories           カテゴリ追加（管理者のみ）
DELETE /api/chuiten/categories/{id}     カテゴリ削除（管理者のみ）

GET    /api/chuiten                      注意点一覧取得
POST   /api/chuiten                      注意点追加（管理者のみ）
GET    /api/chuiten/{id}                 注意点詳細取得
PATCH  /api/chuiten/{id}                 注意点更新（管理者のみ）
DELETE /api/chuiten/{id}                 注意点削除（管理者のみ）

GET    /api/chuiten/by-project/{project_id}  案件関連注意点取得
```

**検索パラメータ**:
- `series`: 対象シリーズで絞り込み
- `category_id`: カテゴリIDで絞り込み
- `keyword`: キーワード検索（注意点内容）

### マスタ管理 (Masters)

各マスタに対して同じCRUD操作が可能。

```
GET    /api/masters/{type}        一覧取得
POST   /api/masters/{type}        新規作成
PUT    /api/masters/{type}/{id}   更新
DELETE /api/masters/{type}/{id}   削除
```

**マスタ種類**:
- `work-category`: 作業区分
- `kishyu`: 機種
- `nounyusaki`: 納入先
- `shinchoku`: 進捗

### 管理者機能 (Admin)

```
GET    /api/admin/users                  全ユーザー一覧
DELETE /api/admin/users/{id}             ユーザー削除
PATCH  /api/admin/users/{id}/activate    ユーザー有効化
PATCH  /api/admin/users/{id}/deactivate  ユーザー無効化
```

**認可**: `is_admin=true` のユーザーのみアクセス可能

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
| 500 | Internal Server Error | サーバーエラー |

## 詳細仕様

AI用の詳細なAPI仕様は `.serena/memories/api_specifications.md` を参照。

## Swagger UI

開発環境では以下のURLでAPIドキュメントを確認できます:
- http://localhost:8000/docs
