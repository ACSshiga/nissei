# Nissei 工数管理システム

製造業向けの工数管理Webアプリケーション

## 概要

既存のGoogle Spreadsheet + Apps Scriptシステムを、FastAPI + Next.jsによるWebアプリケーションに完全移行。

### 主な機能

- 案件管理（管理No・機番・機種・進捗）
- 工数入力（15分刻み、スプレッドシート風UI）
- 請求書生成（CSV出力）
- 資料管理（機種・機番別）
- マスタ管理（作業区分・進捗・納入先等）

## 技術スタック

- **フロントエンド**: Next.js 14 + TypeScript + Tailwind CSS
- **バックエンド**: FastAPI + Python 3.11+
- **データベース**: Supabase PostgreSQL
- **認証**: Supabase Auth
- **ストレージ**: Supabase Storage（本番）/ MinIO（開発）
- **コンテナ**: Docker + Docker Compose

## クイックスタート

### 前提条件

- Docker Desktop
- Node.js 18+
- Python 3.11+

### 起動手順

1. リポジトリをクローン
   ```bash
   git clone https://github.com/ShigaRyunosuke10/nissei.git
   cd nissei
   ```

2. 環境変数設定
   ```bash
   cp .env.example .env
   # .envを編集（Supabase URL/KEYを設定）
   ```

3. Docker起動
   ```bash
   docker-compose up -d
   ```

4. アプリケーションにアクセス
   - フロントエンド: http://localhost:3000
   - バックエンド: http://localhost:8000
   - API Docs: http://localhost:8000/docs

詳細な環境構築手順は [SETUP.md](./SETUP.md) を参照。

## ディレクトリ構造

```
nissei/
├── frontend/          # Next.jsアプリ
├── backend/           # FastAPIアプリ
├── docs/              # ドキュメント（人間用・簡潔版）
│   ├── *.csv          # 参考資料（開発初期のサンプルデータ）
│   └── *.md           # API・DB仕様書
├── .serena/memories/  # AI用詳細仕様
├── reference/         # PDF・Excel等の参考資料
└── docker-compose.yml
```

## ドキュメント

### 人間用（簡潔版）
- [環境構築手順](./SETUP.md)
- [データベース設計](./DATABASE.md)
- [API仕様](./API.md)

### AI用（詳細版）
- `.serena/memories/api_specifications.md` - API詳細仕様
- `.serena/memories/database_specifications.md` - DB詳細仕様
- `.serena/memories/current_issues_and_priorities.md` - 現在の課題・優先度

### 参考資料

プロジェクト関連の参考資料（CSV、Excel、PDF等）は [`reference/`](../reference/) ディレクトリに配置されています。

- `reference/テストシート.csv` - 案件管理の初期サンプルデータ
- `reference/資料作成注意点一覧.csv` - 注意点マスタの参考データ
- `reference/請求書.csv` - 請求書フォーマットの参考
- `reference/2025-9-22.pdf` - 委託書サンプル

## ライセンス

Private - All Rights Reserved
