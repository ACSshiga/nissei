# システムアーキテクチャ

**最終更新**: 2025-10-02
**バージョン**: v2.0

## システム構成図

```
User
  ↓
Next.js Frontend (Supabase Client)
  ↓ HTTP/REST + WebSocket
FastAPI Backend (Supabase Python Client)
  ↓
Supabase PostgreSQL + Auth + RLS
Supabase Storage (prod) / MinIO (dev)
```

---

## 技術スタック

### フロントエンド
- **フレームワーク**: Next.js 14 (App Router)
- **言語**: TypeScript
- **スタイリング**: Tailwind CSS
- **状態管理**: React Hooks + Context API
- **データフェッチング**: Supabase Client (リアルタイム対応)
- **フォーム**: React Hook Form
- **バリデーション**: Zod
- **認証**: Supabase Auth

### バックエンド
- **フレームワーク**: FastAPI
- **言語**: Python 3.11+
- **ORM**: SQLAlchemy + Supabase Python Client
- **マイグレーション**: Supabase Migrations
- **バリデーション**: Pydantic
- **認証**: Supabase Auth (JWT)

### データベース
- **メインDB**: Supabase PostgreSQL
  - Row Level Security (RLS)
  - Realtime subscriptions
  - Auto-generated REST API
- **ファイルストレージ**:
  - 本番: Supabase Storage
  - 開発: MinIO (S3互換)

### インフラ
- **コンテナ**: Docker + Docker Compose
- **CI/CD**: GitHub Actions
- **ホスティング**: TBD (Vercel/Railway/Supabase候補)

---

## ディレクトリ構造

```
nissei/
├── frontend/              # Next.jsフロントエンド
│   ├── src/
│   │   ├── app/          # App Routerページ
│   │   │   ├── login/
│   │   │   ├── register/
│   │   │   ├── dashboard/
│   │   │   ├── projects/
│   │   │   ├── worklogs/
│   │   │   ├── invoices/
│   │   │   ├── materials/
│   │   │   └── masters/
│   │   ├── components/   # 再利用可能コンポーネント
│   │   │   ├── ui/       # 汎用UIコンポーネント
│   │   │   ├── forms/    # フォームコンポーネント
│   │   │   └── layout/   # レイアウトコンポーネント
│   │   ├── lib/          # ユーティリティ・API
│   │   ├── types/        # TypeScript型定義
│   │   └── hooks/        # カスタムフック
│   ├── public/
│   ├── package.json
│   └── tsconfig.json
│
├── backend/              # FastAPIバックエンド
│   ├── app/
│   │   ├── main.py      # エントリーポイント
│   │   ├── api/         # APIエンドポイント
│   │   │   ├── auth.py
│   │   │   ├── projects.py
│   │   │   ├── worklogs.py
│   │   │   ├── invoices.py
│   │   │   ├── materials.py
│   │   │   ├── chuiten.py
│   │   │   ├── masters.py
│   │   │   └── admin.py
│   │   ├── core/        # コア機能
│   │   │   ├── config.py
│   │   │   ├── database.py
│   │   │   └── security.py
│   │   ├── models/      # SQLAlchemyモデル
│   │   ├── schemas/     # Pydanticスキーマ
│   │   └── services/    # ビジネスロジック
│   ├── migrations/      # Supabaseマイグレーション
│   ├── requirements.txt
│   └── Dockerfile
│
├── docs/                # 人間用ドキュメント（簡潔版）
│   ├── README.md
│   ├── SETUP.md
│   ├── DATABASE.md
│   └── API.md
│
├── reference/           # 参考資料（ユーザー提供）
│   ├── 2025-9-22.pdf   # 委託書サンプル
│   ├── テストシート.xlsx
│   ├── 請求書.xlsx
│   └── 資料作成注意点一覧.xlsx
│
├── .serena/memories/    # AI用詳細情報
│   ├── project_overview.md
│   ├── database_specifications.md
│   ├── api_specifications.md
│   ├── system_architecture.md
│   ├── implementation_status.md
│   └── current_issues_and_priorities.md
│
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## データフロー

### 認証フロー

```
1. ユーザー登録・ログイン
   User → Frontend → Backend → Supabase Auth
   ← JWTトークン返却

2. 認証済みリクエスト
   User → Frontend (Header: Bearer token)
        → Backend (JWT検証)
        → Supabase PostgreSQL
   ← データ返却
```

### 工数入力フロー

```
1. 月グリッド取得
   GET /api/worklogs/grid?month=2025-01
   → Supabaseから月全体のwork_logs取得
   ← グリッドデータ返却

2. 差分更新
   PUT /api/worklogs/grid
   { updates: [...], deletes: [...] }
   → Supabaseへ一括更新
   ← 更新結果返却
```

### 請求書生成フロー

```
1. プレビュー
   GET /api/invoices?month=2025-01
   → work_logsから月別集計
   ← 請求明細プレビュー

2. 締め確定
   POST /api/invoices/close
   → invoices + invoice_items作成
   ← 請求書ID返却

3. CSV出力
   GET /api/invoices/export?month=2025-01
   → invoice_itemsからCSV生成
   ← CSVファイルダウンロード
```

### 資料検索フロー

```
1. 機番から階層展開
   機番: HMX7-CN2
   → model: NEX140Ⅲ-24AK
   → tonnage: 140
   → series: NEX

2. スコープ別検索（狭い→広い）
   GET /api/materials?scope=machine&machine_no=HMX7-CN2
   → scope=machine AND machine_no='HMX7-CN2'
   
   GET /api/materials?scope=model&model=NEX140Ⅲ-24AK
   → scope=model AND model='NEX140Ⅲ-24AK'
   
   GET /api/materials?scope=tonnage&series=NEX&tonnage=140
   → scope=tonnage AND series='NEX' AND tonnage=140
   
   GET /api/materials?scope=series&series=NEX
   → scope=series AND series='NEX'
```

---

## 設計判断の理由

### なぜSupabaseか？

1. **認証の統一**: Auth機能で認証を一元管理、JWTトークン自動発行
2. **RLS**: 行レベルセキュリティで権限制御を簡素化
3. **Realtime**: WebSocket不要でリアルタイム更新（将来対応）
4. **Storage**: ファイル保存をシームレス統合
5. **自動REST API**: CRUD操作を自動生成（FastAPIから利用）

### なぜFastAPIも併用するか？

Supabaseだけでなく、FastAPIを併用する理由:

1. **複雑なビジネスロジック**: 工数集計、請求生成、CSV出力など
2. **バッチ処理**: 月締め処理、PDF解析（将来）
3. **カスタムバリデーション**: Pydanticで厳密な型チェック
4. **API統一**: 複雑な処理もRESTful APIで提供
5. **拡張性**: 将来的な機能追加に柔軟対応

### なぜNext.js App Routerか？

1. **SSR/SSG**: SEO対応（将来的な社外公開時）
2. **ファイルベースルーティング**: 直感的なページ構成
3. **TypeScript統合**: 型安全なフロントエンド開発
4. **サーバーコンポーネント**: パフォーマンス最適化
5. **API Routes**: バックエンドとの統合が容易

---

## セキュリティ

### 認証・認可

- **Supabase Auth**: メール + パスワード認証（8文字以上）
- **JWT**: 認証トークン（有効期限: 1時間）
- **RLS**: テーブルレベルのアクセス制御
- **is_admin**: 管理者権限フラグ（請求確定操作等）

### データ保護

- **パスワードハッシュ化**: bcrypt（Supabase自動処理）
- **HTTPS**: 本番環境では必須
- **環境変数**: .envファイルで機密情報管理（Git除外）
- **CORS**: FastAPIで適切に設定

### ファイルアップロード

- **最大サイズ**: 10MB
- **許可形式**: PDF, PNG, JPG, XLSX, DOCX
- **バケットポリシー**: 認証済みユーザーのみアップロード可能

---

## パフォーマンス最適化

### データベース

- 適切なインデックス設定:
  - `projects(management_no)` - UNIQUE
  - `work_logs(project_id, work_date)`
  - `work_logs(user_id, work_date)`
  - `materials(scope, series, tonnage)`
- N+1クエリの回避: Eager Loading使用

### フロントエンド

- コード分割: Next.js動的インポート
- 画像最適化: Next.js Image コンポーネント
- キャッシング: SWR / React Query（将来）
- 遅延ローディング: 初回表示の高速化

### バックエンド

- 非同期処理: FastAPIのasync/await
- バッチ処理: 月締め処理の非同期化
- キャッシング: Redis導入検討（将来）

---

## 環境設定

### 開発環境

```
フロントエンド: http://localhost:3000
バックエンド: http://localhost:8000
PostgreSQL: localhost:5432
MinIO: localhost:9000
```

### 本番環境

```
フロントエンド: TBD (Vercel想定)
バックエンド: TBD (Railway/Fly.io想定)
PostgreSQL: Supabase (wwyrthkizkcgndyorcww)
Storage: Supabase Storage
```

---

## 関連ドキュメント

- データベース仕様: `.serena/memories/database_specifications.md`
- API仕様: `.serena/memories/api_specifications.md`
- 実装状況: `.serena/memories/implementation_status.md`
- 環境構築: `docs/SETUP.md`
