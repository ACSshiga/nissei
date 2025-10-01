# 環境構築手順

## 必要な環境

- Node.js 18以上
- Python 3.11以上
- Docker & Docker Compose
- Git

## クイックスタート

### 1. リポジトリのクローン

```bash
git clone https://github.com/ShigaRyunosuke10/nissei.git
cd nissei
```

### 2. 環境変数の設定

各サービスの `.env.example` をコピーして `.env` を作成：

```bash
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
```

必要な環境変数を設定（`backend/.env`）：

```env
# Supabase
SUPABASE_URL=your-supabase-url
SUPABASE_KEY=your-supabase-key
SUPABASE_PROJECT_REF=wwyrthkizkcgndyorcww

# JWT
JWT_SECRET_KEY=your-secret-key

# その他の設定
```

### 3. Docker Composeで起動

```bash
docker-compose up -d
```

以下のサービスが起動します：
- **フロントエンド**: http://localhost:3000
- **バックエンドAPI**: http://localhost:8000
- **PostgreSQL**: localhost:5432
- **MinIO**: http://localhost:9000

### 4. 動作確認

1. フロントエンドにアクセス
   ```
   http://localhost:3000
   ```

2. バックエンドAPIドキュメント
   ```
   http://localhost:8000/docs
   ```

3. テストユーザーでログイン
   ```
   Email: qa+shared@example.com
   Password: SharedDev!2345
   ```

## ローカル開発（Docker不使用）

### フロントエンド

```bash
cd frontend
npm install
npm run dev
```

### バックエンド

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## ポート設定

⚠️ **以下のポート番号は固定（変更禁止）**

| サービス | ポート | URL |
|---------|--------|-----|
| フロントエンド | 3000 | http://localhost:3000 |
| バックエンド | 8000 | http://localhost:8000 |
| PostgreSQL | 5432 | localhost:5432 |
| MinIO | 9000 | http://localhost:9000 |
| MinIO Console | 9001 | http://localhost:9001 |

### ポート競合時の対応

```bash
# ポート使用状況確認
lsof -i :3000
lsof -i :8000

# プロセスをkill
kill -9 <PID>
```

## データベースセットアップ

### マイグレーション実行

```bash
cd backend
alembic upgrade head
```

### 初期データ投入

⚠️ **注意**: 初期データ投入スクリプトは現在未実装です。
テストユーザーは以下の情報を使用してください：

```
Email: qa+shared@example.com
Password: SharedDev!2345
ユーザー名: qa_shared
ユーザーID: 00000000-0000-4000-8000-000000000000
```

## トラブルシューティング

### Docker起動エラー

```bash
# Docker再起動
docker-compose down
docker-compose up -d --build
```

### データベース接続エラー

1. PostgreSQLが起動しているか確認
   ```bash
   docker ps
   ```

2. 環境変数を確認
   ```bash
   echo $DATABASE_URL
   ```

### フロントエンドビルドエラー

```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### バックエンド起動エラー

```bash
cd backend
rm -rf venv
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 開発ツール

### VS Code推奨拡張機能

- ESLint
- Prettier
- Python
- Tailwind CSS IntelliSense
- Docker

### プロジェクト設定

`.vscode/settings.json` が設定済み：
- フォーマット自動適用
- ESLint自動修正
- Pythonパス設定

## テスト実行

### E2Eテスト

```bash
npx playwright test
```

### フロントエンド単体テスト

```bash
cd frontend
npm test
```

### バックエンド単体テスト

```bash
cd backend
pytest
```

## 次のステップ

- [アーキテクチャ](./ARCHITECTURE.md) - システム設計を理解
- [API仕様](./API.md) - APIエンドポイント一覧
- [データベース設計](./DATABASE.md) - テーブル定義
- [テストガイド](../ai-rules/TESTING.md) - テスト実施方法
