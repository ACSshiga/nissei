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

### 基本フロー
```
セッション開始（Serenaメモリ読み込み）
    ↓
フェーズ・仕様確認
    ↓
ブランチ作成
    ↓
実装・テスト
    ↓
PR作成→レビュー→マージ
    ↓
ドキュメント更新（docs/ + Serenaメモリ）
    ↓
フェーズ完了確認（必要に応じて）
```

詳細は以下を参照：
- [ai-rules/common/WORKFLOW.md](./ai-rules/common/WORKFLOW.md) - 汎用ワークフロー
- [ai-rules/common/PHASE_MANAGEMENT.md](./ai-rules/common/PHASE_MANAGEMENT.md) - フェーズ管理
- [ai-rules/nissei/WORKFLOW.md](./ai-rules/nissei/WORKFLOW.md) - nissei固有ワークフロー

### セッション開始時（必須）
1. **Serenaメモリ読み込み**（最重要）
   ```
   mcp__serena__activate_project
   mcp__serena__list_memories
   mcp__serena__read_memory("current_issues_and_priorities.md")
   mcp__serena__read_memory("phase_progress.md")  # フェーズ管理時
   ```
2. **フェーズ・仕様確認**
   - 現在のフェーズと実装内容を確認
   - 不明点はユーザーに質問

### 作業開始時
1. 専用ブランチを作成（`feat-*`, `fix-*`, `docs-*` 等）
2. mainブランチでの直接作業は絶対禁止

### 作業終了時
1. 変更をコミット（[コミット規約](./ai-rules/common/COMMIT_GUIDELINES.md)に従う）
2. リモートブランチにpush
3. PRを作成（[PR規約](./ai-rules/nissei/PR_AND_REVIEW.md)に従う）
4. **必須**: code-reviewer サブエージェントでレビューを依頼
5. レビュー完了後にmainへマージ
6. **必須**: マージ後の更新（docs/ と .serena/memories/ の両方）

⚠️ **重要**: **PR作成→レビュー→マージ→ドキュメント更新までを1セットの作業として完了させる**

### マージ後の必須作業
1. **docs/ の更新**: API.md, DATABASE.md など人間用ドキュメントを更新
2. **Serenaメモリの更新**: `.serena/memories/` 内のAI用詳細仕様を更新
   - 変更に応じて該当メモリファイルを更新（api_specifications.md, database_specifications.md等）
   - phase_progress.md の進捗を更新（フェーズ管理時）
   - 必要に応じて current_issues_and_priorities.md も更新

### フェーズ完了時（該当する場合）
1. **仕様との整合性確認**（ユーザーと最終確認）
2. 全機能の動作確認・E2Eテスト
3. ドキュメント完全更新（docs/PHASES.md + Serenaメモリ）
4. 次フェーズの準備

## コミット前の必須確認

- 動作確認を実施
- E2Eテストを実施（[テストガイド](./ai-rules/nissei/TESTING.md)）
- エラーがない状態でコミット

## 命名規則

詳細は [ai-rules/common/NAMING_CONVENTIONS.md](./ai-rules/common/NAMING_CONVENTIONS.md) を参照。

### 主要ルール
- **TypeScript/JavaScript**: camelCase（変数・関数）、PascalCase（クラス・型）
- **Python**: snake_case（変数・関数）、PascalCase（クラス）
- **APIエンドポイント**: kebab-case（小文字）、複数形の名詞
- **環境変数**: UPPER_SNAKE_CASE（クォート無し）
- **データベース**: snake_case（テーブル・カラム）

## テスト

詳細は [ai-rules/nissei/TESTING.md](./ai-rules/nissei/TESTING.md) を参照。

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

詳細は [ai-rules/nissei/PR_AND_REVIEW.md](./ai-rules/nissei/PR_AND_REVIEW.md) を参照。

### レビュー方法（必須）
1. PR作成直後に **code-reviewer サブエージェント**でレビュー依頼（自動または明示的）
2. レビュー結果を評価（Critical/Major/Minor）
3. 指摘事項を確認し、必要に応じて修正・Issue化
4. レビュー承認後にmainへマージ

**サブエージェント設定**: `.claude/agents/code-reviewer.md` に定義

## MCPサーバー

詳細は [ai-rules/nissei/SETUP_AND_MCP.md](./ai-rules/nissei/SETUP_AND_MCP.md) を参照。

### 利用可能なMCP
- **context7**: RAG/検索支援
- **playwright**: E2Eテスト自動化
- **github**: Issue/PR操作
- **desktop-commander**: ローカルPC操作
- **serena**: コードベース解析・メモリ管理（**推奨**）
- **supabase**: DB/認証/ストレージ連携

### カスタムサブエージェント
- **code-reviewer** (`.claude/agents/code-reviewer.md`): PRレビュー専門エージェント

## Serena MCP活用（重要）

**最重要**: 毎セッション開始時にSerenaメモリから状況を把握すること。

### セッション開始時の必須フロー
```
1. mcp__serena__activate_project
2. mcp__serena__list_memories
3. mcp__serena__read_memory("current_issues_and_priorities.md")
4. 作業開始
```

### Serenaメモリファイル一覧（8個）
- `current_issues_and_priorities.md` - 現在のIssue・優先度（**最重要**）
- `project_overview.md` - プロジェクト概要
- `database_specifications.md` - DB詳細仕様
- `api_specifications.md` - API詳細仕様
- `system_architecture.md` - システムアーキテクチャ
- `implementation_status.md` - 実装状況・進捗
- `material_and_chuiten_specifications.md` - 資料・注意点仕様
- `database_api_specifications.md` - 統合仕様（互換性用）

詳細は [ai-rules/nissei/DOCUMENTATION_GUIDE.md](./ai-rules/nissei/DOCUMENTATION_GUIDE.md) を参照

### いつSerenaを使うか
- ✅ セッション開始時（メモリ読み込み）
- ✅ プロジェクト全体把握
- ✅ 複数ファイルにまたがる変更
- ✅ 影響範囲調査
- ❌ 1-2個のファイルの簡単な編集（通常ツールで十分）

詳細: [ai-rules/nissei/SETUP_AND_MCP.md](./ai-rules/nissei/SETUP_AND_MCP.md)

## Context7利用

最新ライブラリ仕様を反映させたい場合に使用。

```
use context7 — [質問内容]
```

## プロジェクト固有情報

以下は `docs/` ディレクトリを参照：

- [プロジェクト概要](./docs/README.md)
- [環境構築手順](./docs/SETUP.md)
- [API仕様（簡潔版）](./docs/API.md)
- [データベース設計（簡潔版）](./docs/DATABASE.md)

詳細な技術仕様は `.serena/memories/` を参照（[ドキュメント管理ガイド](./ai-rules/nissei/DOCUMENTATION_GUIDE.md)）

## ファイル構造

```
nissei/
├── CLAUDE.md              # このファイル（AI用設定）
├── README.md              # プロジェクト概要（人間用）
├── .claude/agents/        # カスタムサブエージェント
├── ai-rules/              # AI用開発ガイドライン（2層構造）
│   ├── common/            # プロジェクト横断（汎用）
│   └── nissei/            # nissei 専用
├── docs/                  # 人間用ドキュメント（簡潔版）
├── .serena/memories/      # AI用詳細仕様（Serenaメモリ）
├── reference/             # 参考資料（PDF・Excel等）
├── frontend/              # Next.jsアプリ
├── backend/               # FastAPIアプリ
└── docker-compose.yml
```

詳細なディレクトリ構造: [ai-rules/README.md](./ai-rules/README.md)

## 注意事項

- .envファイルはUPPER_SNAKE_CASE、値にクォート無し
- 機密情報は.gitignoreに追加
- ファイル作成時はGitにコミットすべきか判断し、不要なら.gitignoreへ
