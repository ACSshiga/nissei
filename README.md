# Nissei 工数管理システム

工数管理と請求処理のためのWebアプリケーション（MVP版）

## 技術スタック

### バックエンド
- **FastAPI** (Python 3.11)
- **PostgreSQL 15** (データベース)
- **SQLAlchemy** (ORM)
- **JWT認証**
- **MinIO** (S3互換ストレージ)

### フロントエンド
- **Next.js 14** (App Router)
- **TypeScript**
- **Tailwind CSS**
- **React Query**

### インフラ
- **Docker Compose**

## セットアップ

### 前提条件
- Docker Desktop がインストールされていること
- Git がインストールされていること

### 起動手順

1. リポジトリをクローン
```bash
git clone <repository-url>
cd nissei
```

2. 環境変数ファイルをコピー
```bash
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
```

3. Docker Composeで起動
```bash
docker-compose up -d
```

4. ブラウザでアクセス
- フロントエンド: http://localhost:3000
- バックエンドAPI: http://localhost:8000
- MinIO Console: http://localhost:9001

## プロジェクト構造

```
nissei/
├── backend/              # FastAPI バックエンド
│   ├── app/
│   │   ├── api/         # APIエンドポイント
│   │   ├── core/        # コア設定
│   │   ├── models/      # データベースモデル
│   │   ├── schemas/     # Pydanticスキーマ
│   │   └── services/    # ビジネスロジック
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/             # Next.js フロントエンド
│   ├── src/
│   │   ├── app/         # App Router
│   │   ├── components/  # Reactコンポーネント
│   │   └── lib/         # ユーティリティ
│   ├── Dockerfile
│   └── package.json
├── docker-compose.yml    # Docker Compose設定
└── requirements.md       # 要件定義書
```

## 主な機能

1. **認証システム**
   - メール・パスワードによる独自認証
   - JWT トークン認証

2. **案件管理**
   - PDF取込による案件自動登録
   - 案件詳細管理

3. **工数入力**
   - 月グリッドUI（Excel風）
   - 日別工数入力

4. **請求処理**
   - 月次請求締め処理
   - Excel出力

5. **資料管理**
   - 機種/機番ごとの資料管理
   - URL・ファイル対応

6. **注意点チェックリスト**
   - テンプレート管理
   - 案件別チェック項目

## 開発

### バックエンド開発

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### フロントエンド開発

```bash
cd frontend
npm install
npm run dev
```

## API ドキュメント

バックエンドを起動後、以下のURLでAPI ドキュメントを参照できます：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## ライセンス

Private - All Rights Reserved