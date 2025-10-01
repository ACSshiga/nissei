# 日誠（にっせい） - 建設プロジェクト管理システム

建設プロジェクトの工事進捗、作業履歴、請求書、資材管理を一元管理するWebアプリケーションです。

## 🚀 クイックスタート

```bash
# リポジトリのクローン
git clone https://github.com/ShigaRyunosuke10/nissei.git
cd nissei

# 環境変数の設定
cp .env.example .env
# .envを編集して必要な値を設定

# Docker Composeで起動
docker-compose up -d

# アクセス
# フロントエンド: http://localhost:3000
# バックエンドAPI: http://localhost:8000
```

詳細は [環境構築手順](./docs/SETUP.md) を参照してください。

## ✨ 主な機能

### プロジェクト管理
- プロジェクトの作成・編集・削除
- ステータス管理（計画中・進行中・完了）
- 開始日・終了日の設定

### 作業履歴管理
- 日次の作業内容を記録
- 作業時間の管理
- プロジェクトごとの作業履歴一覧

### 請求書管理
- 請求書の作成・送信
- 請求書番号の自動採番
- ステータス管理（下書き・送信済み・支払済み）

### 資材管理
- 資材の登録・編集
- カテゴリ別の管理
- 単価・数量の管理

### チェックリスト
- プロジェクトごとのタスク管理
- 完了状態の管理

## 🛠 技術スタック

### フロントエンド
- **Next.js 14** (App Router)
- **TypeScript**
- **Tailwind CSS**
- **SWR** (データフェッチング)

### バックエンド
- **FastAPI**
- **Python 3.11+**
- **SQLAlchemy** (ORM)
- **Pydantic** (バリデーション)
- **JWT認証**

### データベース
- **Supabase** (PostgreSQL)
- **MinIO** (ファイルストレージ)

### インフラ
- **Docker** & **Docker Compose**
- **GitHub Actions** (CI/CD)

## 📁 プロジェクト構造

```
nissei/
├── frontend/          # Next.jsフロントエンド
├── backend/           # FastAPIバックエンド
├── docs/              # プロジェクト固有ドキュメント
├── ai-rules/          # AI用開発ルール（汎用）
├── CLAUDE.md          # Claude Code設定
└── docker-compose.yml
```

## 📚 ドキュメント

### 開発者向け
- [環境構築手順](./docs/SETUP.md)
- [システムアーキテクチャ](./docs/ARCHITECTURE.md)
- [API仕様書](./docs/API.md)
- [データベース設計](./docs/DATABASE.md)

### 開発ルール
- [ワークフロー](./ai-rules/WORKFLOW.md)
- [コミット規約](./ai-rules/COMMIT_GUIDELINES.md)
- [PR作成ルール](./ai-rules/PR_GUIDELINES.md)
- [命名規則](./ai-rules/NAMING_CONVENTIONS.md)
- [コードレビュー](./ai-rules/CODE_REVIEW.md)
- [テストガイド](./ai-rules/TESTING.md)

## 🔐 認証

JWTトークンベースの認証システムを採用。

### テストユーザー
```
Email: qa+shared@example.com
Password: SharedDev!2345
```

## 🧪 テスト

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

## 🤝 コントリビューション

### 開発フロー

1. **ブランチ作成**
   ```bash
   git checkout -b feat-新機能名
   ```

2. **開発・テスト**
   - コミット前にE2Eテストを実施
   - エラーがない状態でコミット

3. **PR作成**
   - GitHub PRを作成
   - `@codex review` コメントを投稿してCodexレビューを依頼

4. **マージ**
   - Codexレビュー承認後にmainへマージ

詳細は [ワークフロー](./ai-rules/WORKFLOW.md) を参照。

## 📞 サポート

### Discord通知
PRコメント・Codexレビューは自動的にDiscordへ通知されます。
- チャンネル: `#github-notifications`

### リポジトリ
- GitHub: [ShigaRyunosuke10/nissei](https://github.com/ShigaRyunosuke10/nissei)

## 📝 ライセンス

Private - All Rights Reserved

## 📌 ポート設定

| サービス | ポート | URL |
|---------|--------|-----|
| フロントエンド | 3000 | http://localhost:3000 |
| バックエンド | 8000 | http://localhost:8000 |
| PostgreSQL | 5432 | localhost:5432 |
| MinIO | 9000 | http://localhost:9000 |

⚠️ **ポート番号は固定**：変更禁止

## 🔗 関連リンク

- [要件定義書](./docs/requirements-definition.md)
- [機械学習分類アルゴリズム](./docs/machine-classification-algorithm.md)

---

Built with ❤️ by the Nissei Team
