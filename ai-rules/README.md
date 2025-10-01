# AI Rules - 開発ガイドライン

このディレクトリには、nissei プロジェクトの開発ガイドラインが格納されています。

**最終更新**: 2025-10-01

---

## 📚 ドキュメント構成

### 🔄 ワークフロー関連

1. **[WORKFLOW.md](./WORKFLOW.md)** - 開発ワークフロー全体
   - 作業開始から終了までの流れ
   - ブランチ作成、コミット、PR作成、レビュー、マージの全工程

2. **[PR_MERGE_PROCESS.md](./PR_MERGE_PROCESS.md)** - PRマージプロセス
   - Codex MCP によるレビュー方法
   - レビュー結果の評価基準
   - Issue作成とマージ実行の詳細手順

3. **[PR_GUIDELINES.md](./PR_GUIDELINES.md)** - PR作成ガイドライン
   - PRテンプレート（新機能、バグ修正、リファクタリング）
   - PR作成前のチェックリスト

4. **[COMMIT_GUIDELINES.md](./COMMIT_GUIDELINES.md)** - コミットメッセージガイドライン
   - コミットメッセージの形式（type, subject, body）
   - コミット前の確認事項

---

### 🔍 コードレビュー関連

5. **[CODE_REVIEW.md](./CODE_REVIEW.md)** - コードレビューチェックリスト
   - レビュー観点（セキュリティ、パフォーマンス、コード品質、テスト、ドキュメント）
   - セルフレビューのポイント

---

### 🐛 Issue管理

6. **[ISSUE_GUIDELINES.md](./ISSUE_GUIDELINES.md)** - Issue作成ガイドライン
   - Issueテンプレート（バグ報告、PRレビュー指摘、新機能追加、リファクタリング）
   - ラベル分類と優先度設定

---

### 🧪 テスト関連

7. **[TESTING.md](./TESTING.md)** - テストガイドライン
   - E2Eテスト実施手順（Playwright MCP使用）
   - テストユーザー情報
   - テストケース作成ガイドライン

---

### 📝 命名規則

8. **[NAMING_CONVENTIONS.md](./NAMING_CONVENTIONS.md)** - 命名規則
   - ファイル・ディレクトリ命名
   - 変数・関数命名
   - APIエンドポイント命名
   - データベーステーブル・カラム命名
   - 環境変数命名

---

### 🔧 MCP サーバー運用

9. **[MCP_USAGE.md](./MCP_USAGE.md)** - MCP サーバー運用ガイド
   - context7（RAG/検索支援）
   - playwright（E2E自動テスト）
   - github（Issue/PR操作）
   - desktop-commander（ローカルPC操作）
   - serena（高度な自動化）
   - supabase（DB/認証/ストレージ）
   - codex（深掘り解析・アーキテクチャ相談）

---

## 🚀 クイックスタート

### 新規タスクを開始する場合

1. [WORKFLOW.md](./WORKFLOW.md) を読んで全体の流れを把握
2. ブランチを作成（`feat-*`, `fix-*`）
3. 実装・修正を行う
4. [TESTING.md](./TESTING.md) に従ってE2Eテストを実施
5. [COMMIT_GUIDELINES.md](./COMMIT_GUIDELINES.md) に従ってコミット
6. [PR_GUIDELINES.md](./PR_GUIDELINES.md) に従ってPR作成
7. [PR_MERGE_PROCESS.md](./PR_MERGE_PROCESS.md) に従ってCodex MCPレビューを依頼
8. レビュー承認後、mainブランチへマージ

### コードレビューを実施する場合

1. [CODE_REVIEW.md](./CODE_REVIEW.md) でチェック項目を確認
2. [PR_MERGE_PROCESS.md](./PR_MERGE_PROCESS.md) に従ってCodex MCPにレビュー依頼
3. レビュー結果を評価（Critical/Major/Minor）
4. 必要に応じて [ISSUE_GUIDELINES.md](./ISSUE_GUIDELINES.md) に従ってIssue作成

### バグを発見した場合

1. [ISSUE_GUIDELINES.md](./ISSUE_GUIDELINES.md) に従ってIssue作成
2. [WORKFLOW.md](./WORKFLOW.md) に従って修正用ブランチを作成
3. 修正後、E2Eテストで動作確認
4. PR作成してCodex MCPレビュー

---

## 📖 ドキュメント間の関係

```
WORKFLOW.md (全体の流れ)
    ├── COMMIT_GUIDELINES.md (コミット)
    ├── PR_GUIDELINES.md (PR作成)
    ├── PR_MERGE_PROCESS.md (レビュー・マージ)
    │   ├── CODE_REVIEW.md (レビュー観点)
    │   ├── ISSUE_GUIDELINES.md (Issue作成)
    │   └── MCP_USAGE.md (Codex MCP使用方法)
    ├── TESTING.md (テスト実施)
    │   └── MCP_USAGE.md (Playwright MCP使用方法)
    └── NAMING_CONVENTIONS.md (命名規則)
```

---

## 🔗 外部ドキュメント

- [../CLAUDE.md](../CLAUDE.md): Claude Code 設定と全体ルール
- [../docs/PR_REVIEW_HISTORY.md](../docs/PR_REVIEW_HISTORY.md): PRレビュー履歴

---

## ⚠️ 重要な注意事項

- **mainブランチへの直接作業は絶対禁止**
- **コミット前に必ず動作確認とE2Eテストを実施**
- **PR作成直後に必ずCodex MCPレビューを依頼**
- **Critical問題が存在する場合は絶対にマージしない**
- **機密情報（APIキー、パスワード等）はコミットしない**

---

## 📝 更新履歴

- **2025-10-01**: 全ドキュメントを整理・統合
  - Codex MCP による実際のレビューフローに合わせて更新
  - 重複を削除し、相互参照を明確化
  - ISSUE_GUIDELINES.md を新規作成
  - README.md（このファイル）を新規作成
