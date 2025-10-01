# 開発ワークフロー

このドキュメントでは、作業開始から終了までの全体的なワークフローを定義します。

---

## 作業開始時（必須）

### ブランチ作成
**必ず専用ブランチを作成する**

```bash
git checkout -b <ブランチ名>
```

#### ブランチ命名規則
- `feat-<機能名>`: 新機能追加（例: `feat-user-dashboard`）
- `fix-<修正内容>`: バグ修正（例: `fix-login-timeout`）
- `refactor-<対象>`: リファクタリング（例: `refactor-api-error-handling`）
- `docs-<内容>`: ドキュメント更新（例: `docs-api-specification`）

#### ⚠️ 重要
**mainブランチでの直接作業は絶対禁止**
- いかなる変更もmainブランチに直接コミットしない

---

## 作業中

### 慎重な修正
- **該当修正によって他の処理に問題がないか確認**
- 他の動作に影響がある場合は既存の期待動作が正常に動作するよう修正
- 修正前に影響範囲を把握する

### コミット前の確認（必須）

#### 動作確認
- **必ず動作確認を行う**
  - 動作確認中にエラーが発見された際はタスクを更新
  - エラーがない状態でコミット

#### E2Eテスト
- **[Playwright MCP](./TESTING.md) を使用してテスト実施**
  - ユーザー目線での動作を確認
  - テストユーザーで全フローを確認
  - スクリーンショットを保存

#### セルフチェック
- [ ] コンソールエラーがない
- [ ] デバッグコード（`console.log`, `print`）を削除
- [ ] 不要なコメントを削除
- [ ] コードフォーマットが統一されている
- [ ] [命名規則](./NAMING_CONVENTIONS.md) に準拠している

---

## 作業終了時（必須）

### 1. 変更をコミット

```bash
git add .
git commit -m "<type>: <subject>

<body>

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

**コミットメッセージの詳細**: [COMMIT_GUIDELINES.md](./COMMIT_GUIDELINES.md)

### 2. リモートブランチにpush

```bash
git push -u origin <ブランチ名>
```

### 3. PR作成

```bash
# MCP GitHub APIを使用
mcp__github__create_pull_request
  owner: "ACSshiga"
  repo: "nissei"
  title: "<type>: <変更内容の要約>"
  body: "
## 概要
...

## 変更内容
- ...

## テスト手順
1. ...

## 関連Issue
Closes #XX
"
  head: "<ブランチ名>"
  base: "main"
```

**PRテンプレートの詳細**: [PR_GUIDELINES.md](./PR_GUIDELINES.md)

### 4. Claude Code サブエージェント (Task tool) レビュー依頼（必須）

⚠️ **重要**: PR作成直後に必ず実施

Task toolを使用してレビュー依頼を行います。

**レビュープロセスの詳細**: [PR_MERGE_PROCESS.md](./PR_MERGE_PROCESS.md)

### 5. レビュー対応（指摘事項がある場合）

#### 修正を実施

1. **指摘事項を確認**
   - Critical/Major/Minorの分類を確認
   - 優先度に基づいて対応計画を立てる

2. **修正作業**
   ```bash
   # 修正
   git add .
   git commit -m "fix: レビュー指摘事項を修正

   - Critical: ...
   - Major: ...

   🤖 Generated with [Claude Code](https://claude.com/claude-code)

   Co-Authored-By: Claude <noreply@anthropic.com>"
   git push
   ```

3. **再レビュー依頼**
   - PR更新後、再度Claude Code サブエージェント (Task tool) にレビュー依頼
   - 修正内容をPRコメントで報告（推奨）

4. **修正完了まで繰り返し**
   - すべてのCritical/Major問題が解決されるまで「修正 → push → Claude Code サブエージェント (Task tool) レビュー」を繰り返す

### 6. マージ（レビュー承認後）

⚠️ **重要**: **PR作成→レビュー→マージまでを1セットの作業として完了させる**
- PRが溜まると干渉したり競合の原因になるため、必ずマージまで完了させる

#### マージ前の確認

```bash
# PR状態を確認
mcp__github__get_pull_request
  owner: "ACSshiga"
  repo: "nissei"
  pullNumber: <PR番号>

# 確認項目:
# - mergeable: true
# - レビューが承認済み
# - すべてのCritical問題が解決済み
```

#### mainブランチへマージ

```bash
# MCP GitHub APIを使用
mcp__github__merge_pull_request
  owner: "ACSshiga"
  repo: "nissei"
  pullNumber: <PR番号>
  merge_method: "squash"  # 推奨
```

#### マージ後のクリーンアップ（任意）

```bash
# ローカルブランチ削除
git checkout main
git branch -d <ブランチ名>

# リモートブランチ削除
git push origin --delete <ブランチ名>
```

**マージプロセスの詳細**: [PR_MERGE_PROCESS.md](./PR_MERGE_PROCESS.md)

### 7. docs/ ディレクトリの更新確認（マージ後必須）

⚠️ **重要**: **1セットの作業完了時に必ず docs/ の更新が必要か確認する**

#### 確認が必要な変更
- データベーススキーマ変更（テーブル追加・カラム変更など）
- API エンドポイント追加・変更（リクエスト/レスポンス形式変更）
- 環境変数の追加・変更
- 新機能の追加（アーキテクチャへの影響）
- 設定ファイルの変更

#### 更新対象ドキュメント
- **[docs/DATABASE.md](../docs/DATABASE.md)**: データベーススキーマ定義
- **[docs/API.md](../docs/API.md)**: API エンドポイント仕様
- **[docs/SETUP.md](../docs/SETUP.md)**: 環境構築手順
- **[docs/ARCHITECTURE.md](../docs/ARCHITECTURE.md)**: システムアーキテクチャ

#### 更新フロー

```bash
# 1. 変更内容を確認し、docs/ 更新が必要か判断
# 2. 必要な場合は新しいブランチを作成
git checkout main
git pull
git checkout -b docs-update-<内容>

# 3. ドキュメントを更新
# 4. コミット・push・PR作成
# 5. Claude Code サブエージェント (Task tool) レビュー → マージ（通常フロー）
```

---

## ワークフロー図

```
[作業開始]
    ↓
[ブランチ作成] (feat-*, fix-*)
    ↓
[実装・修正]
    ↓
[動作確認 + E2Eテスト] ← 必須
    ↓
[コミット] (COMMIT_GUIDELINES.md準拠)
    ↓
[push]
    ↓
[PR作成] (PR_GUIDELINES.md準拠)
    ↓
[Claude Code サブエージェント (Task tool) レビュー依頼] ← 必須
    ↓
[レビュー結果確認]
    ├─[マージ可] → [マージ] → [docs/ 更新確認] ← 必須
    │                              ↓
    │                         [更新不要] → [完了]
    │                              ↓
    │                         [更新必要] → [ブランチ作成] → ループ
    │
    └─[要修正] → [修正] → [push] → [再レビュー依頼] → ループ
```

---

## 詳細ガイドライン

各工程の詳細は以下のドキュメントを参照してください：

- [COMMIT_GUIDELINES.md](./COMMIT_GUIDELINES.md): コミットメッセージガイドライン
- [PR_GUIDELINES.md](./PR_GUIDELINES.md): PR作成ガイドライン
- [PR_MERGE_PROCESS.md](./PR_MERGE_PROCESS.md): PRレビュー・マージプロセス
- [CODE_REVIEW.md](./CODE_REVIEW.md): コードレビューチェックリスト
- [TESTING.md](./TESTING.md): テストガイドライン
- [NAMING_CONVENTIONS.md](./NAMING_CONVENTIONS.md): 命名規則
- [ISSUE_GUIDELINES.md](./ISSUE_GUIDELINES.md): Issue作成ガイドライン
- [MCP_USAGE.md](./MCP_USAGE.md): MCP サーバー運用ガイド

---

## 注意事項

- ⚠️ **mainブランチへの直接作業は絶対禁止**
- ⚠️ **コミット前に必ず動作確認とE2Eテストを実施**
- ⚠️ **PR作成直後に必ずClaude Code サブエージェント (Task tool) レビューを依頼**
- ⚠️ **Critical問題が存在する場合は絶対にマージしない**
- ⚠️ **PR作成→レビュー→マージまでを1セットの作業として完了させる**（PRを溜めない）
- ⚠️ **マージ後は必ず docs/ の更新が必要か確認する**
