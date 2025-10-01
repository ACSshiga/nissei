# Claude Code Configuration

このファイルはClaude Codeの動作設定を定義します。

## 基本ルール

- 回答は日本語で行う
- TODO管理を活用してタスク進行を可視化
- 全TODO完了時は通知音を再生

## リポジトリ設定

- **リポジトリ名**: nissei
- **Owner**: ShigaRyunosuke10
- **Git remote**: origin

## ポート設定（固定・変更禁止）

| サービス | ポート |
|---------|--------|
| フロントエンド | 3000 |
| バックエンド | 8000 |

ポート競合時は他のプロセスをkillして既定ポートを使用すること。

## 開発ワークフロー

詳細は [ai-rules/WORKFLOW.md](./ai-rules/WORKFLOW.md) を参照。

### 作業開始時
1. 専用ブランチを作成（`feat-*`, `fix-*`, `docs-*` 等）
2. mainブランチでの直接作業は絶対禁止

### 作業終了時
1. 変更をコミット（[コミット規約](./ai-rules/COMMIT_GUIDELINES.md)に従う）
2. リモートブランチにpush
3. PRを作成（[PR規約](./ai-rules/PR_GUIDELINES.md)に従う）
4. **必須**: Task tool（general-purposeサブエージェント）でレビューを依頼
5. レビュー完了後にmainへマージ

## コミット前の必須確認

- 動作確認を実施
- E2Eテストを実施（[テストガイド](./ai-rules/TESTING.md)）
- エラーがない状態でコミット

## 命名規則

詳細は [ai-rules/NAMING_CONVENTIONS.md](./ai-rules/NAMING_CONVENTIONS.md) を参照。

### 主要ルール
- **TypeScript/JavaScript**: camelCase（変数・関数）、PascalCase（クラス・型）
- **Python**: snake_case（変数・関数）、PascalCase（クラス）
- **APIエンドポイント**: kebab-case（小文字）、複数形の名詞
- **環境変数**: UPPER_SNAKE_CASE（クォート無し）
- **データベース**: snake_case（テーブル・カラム）

## テスト

詳細は [ai-rules/TESTING.md](./ai-rules/TESTING.md) を参照。

### テストユーザー情報
```
Email: qa+shared@example.com
Password: SharedDev!2345
Username: qa_shared
User ID: 00000000-0000-4000-8000-000000000000
```

### E2Eテスト実施
- Playwright MCPツールを使用
- コミット前に必ず実施

## コードレビュー

詳細は [ai-rules/CODE_REVIEW.md](./ai-rules/CODE_REVIEW.md) を参照。

### レビュー方法（必須）
1. PR作成直後に Task tool（general-purposeサブエージェント）でレビュー依頼
2. サブエージェントが最新コミットを自動確認
3. 指摘事項を確認し、必要に応じて修正

## MCPサーバー

詳細は [ai-rules/MCP_USAGE.md](./ai-rules/MCP_USAGE.md) を参照。

### 利用可能なMCP
- **context7**: RAG/検索支援
- **playwright**: E2Eテスト自動化
- **github**: Issue/PR操作
- **desktop-commander**: ローカルPC操作
- **serena**: 高度な自動化
- **supabase**: DB/認証/ストレージ連携

## Context7利用

最新ライブラリ仕様を反映させたい場合に使用。

```
use context7 — [質問内容]
```

## プロジェクト固有情報

以下は `docs/` ディレクトリを参照：

- [環境構築手順](./docs/SETUP.md)
- [システムアーキテクチャ](./docs/ARCHITECTURE.md)
- [API仕様](./docs/API.md)
- [データベース設計](./docs/DATABASE.md)
- [要件定義](./docs/requirements-definition.md)

## ファイル構造

```
nissei/
├── CLAUDE.md              # このファイル（AI用設定）
├── README.md              # プロジェクト概要（人間用）
├── ai-rules/              # AI用汎用ルール
│   ├── WORKFLOW.md
│   ├── COMMIT_GUIDELINES.md
│   ├── PR_GUIDELINES.md
│   ├── NAMING_CONVENTIONS.md
│   ├── CODE_REVIEW.md
│   ├── TESTING.md
│   ├── NOTIFICATION_SETUP.md
│   └── MCP_USAGE.md
├── docs/                  # プロジェクト固有情報
│   ├── SETUP.md
│   ├── ARCHITECTURE.md
│   ├── API.md
│   └── DATABASE.md
├── frontend/              # Next.jsアプリ
├── backend/               # FastAPIアプリ
└── docker-compose.yml
```

## 注意事項

- .envファイルはUPPER_SNAKE_CASE、値にクォート無し
- 機密情報は.gitignoreに追加
- ファイル作成時はGitにコミットすべきか判断し、不要なら.gitignoreへ
