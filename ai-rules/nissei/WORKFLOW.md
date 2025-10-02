# 開発ワークフロー（nissei 専用）

このドキュメントでは、作業開始から終了までの全体的なワークフローを定義します。

**プロジェクト固有**: このファイルは nissei プロジェクト専用の設定を含みます。

**最終更新**: 2025-10-02

---

## クイックリファレンス

### 全体フロー図

```
[作業開始]
    ↓
[ブランチ作成] (feat-*, fix-*, docs-*, refactor-*)
    ↓
[実装・修正]
    ↓
[動作確認 + E2Eテスト] ← 必須（TESTING.md）
    ↓
[コミット] ← COMMIT_GUIDELINES.md準拠
    ↓
[push]
    ↓
[PR作成] ← PR_AND_REVIEW.md参照
    ↓
[code-reviewer サブエージェント レビュー依頼] ← 必須
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

## 1. 作業開始時（必須）

### 1.1 Serena メモリから状態を読み込み

⚠️ **重要**: 毎セッション開始時に必ず実施

```
1. mcp__serena__activate_project
   project: "nissei"

2. mcp__serena__list_memories
   → 利用可能なメモリを確認

3. mcp__serena__read_memory
   memory_file_name: "current_issues_and_priorities.md"
   → 現在の優先度を把握

4. 作業開始
```

詳細: [SETUP_AND_MCP.md](./SETUP_AND_MCP.md) の「Serena MCP」セクション

### 1.2 ブランチ作成

**必ず専用ブランチを作成する**

```bash
git checkout -b <ブランチ名>
```

#### ブランチ命名規則

- `feat-<機能名>`: 新機能追加（例: `feat-user-dashboard`）
- `fix-<修正内容>`: バグ修正（例: `fix-login-timeout`）
- `refactor-<対象>`: リファクタリング（例: `refactor-api-error-handling`）
- `docs-<内容>`: ドキュメント更新（例: `docs-api-specification`）

⚠️ **重要**: mainブランチでの直接作業は絶対禁止

---

## 2. 実装・修正

### 2.1 命名規則に準拠

詳細: [NAMING_CONVENTIONS.md](./NAMING_CONVENTIONS.md)

- TypeScript/JavaScript: camelCase（変数・関数）、PascalCase（クラス・型）
- Python: snake_case（変数・関数）、PascalCase（クラス）
- APIエンドポイント: kebab-case、複数形の名詞
- データベース: snake_case（テーブル・カラム）
- 環境変数: UPPER_SNAKE_CASE

### 2.2 影響範囲の確認

- 該当修正によって他の処理に問題がないか確認
- 他の動作に影響がある場合は既存の期待動作が正常に動作するよう修正
- 修正前に影響範囲を把握する

---

## 3. テスト（必須）

詳細: [TESTING.md](./TESTING.md)

### 3.1 動作確認

- **必ず動作確認を行う**
- 動作確認中にエラーが発見された際はタスクを更新
- エラーがない状態でコミット

### 3.2 E2Eテスト

- **Playwright MCP を使用してテスト実施**
- ユーザー目線での動作を確認
- テストユーザー（qa+shared@example.com）で全フローを確認
- スクリーンショットを保存

### 3.3 セルフチェック

- [ ] コンソールエラーがない
- [ ] デバッグコード（`console.log`, `print`）を削除
- [ ] 不要なコメントを削除
- [ ] コードフォーマットが統一されている
- [ ] [命名規則](./NAMING_CONVENTIONS.md) に準拠している

---

## 4. コミット

詳細: [COMMIT_GUIDELINES.md](./COMMIT_GUIDELINES.md)

### 4.1 コミットメッセージ形式

```bash
git add .
git commit -m "<type>: <subject>

<body>

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

#### Type（必須）

- `feat`: 新機能追加
- `fix`: バグ修正
- `docs`: ドキュメントのみの変更
- `refactor`: バグ修正や機能追加を含まないコードの変更
- `test`: テストの追加・修正
- `chore`: ビルドプロセスやツールの変更

---

## 5. PR作成・レビュー・マージ

⚠️ **重要**: このフェーズの詳細は **[PR_AND_REVIEW.md](./PR_AND_REVIEW.md)** を参照してください

### 5.1 push

```bash
git push -u origin <ブランチ名>
```

### 5.2 PR作成

```bash
mcp__github__create_pull_request
  owner: "ShigaRyunosuke10"
  repo: "nissei"
  title: "<type>: <変更内容の要約>"
  body: "[PR_AND_REVIEW.md のテンプレートに従う]"
  head: "<ブランチ名>"
  base: "main"
```

### 5.3 code-reviewer サブエージェント レビュー（必須）

PR作成直後に必ず実施

```
> code-reviewerサブエージェントを使用してPR #[番号]をレビューしてください
```

### 5.4 レビュー対応

- **マージ可**: マージ実行 → docs/ 更新確認
- **要修正**: 修正 → push → 再レビュー依頼

### 5.5 マージ

```bash
mcp__github__merge_pull_request
  owner: "ShigaRyunosuke10"
  repo: "nissei"
  pullNumber: <PR番号>
  merge_method: "squash"  # 推奨
```

---

## 6. docs/ ディレクトリの更新確認（マージ後必須）

⚠️ **重要**: PR作成→レビュー→マージまでを1セットの作業として完了させる

### 6.1 確認が必要な変更

- データベーススキーマ変更（テーブル追加・カラム変更など）
- API エンドポイント追加・変更（リクエスト/レスポンス形式変更）
- 環境変数の追加・変更
- 新機能の追加（アーキテクチャへの影響）
- 設定ファイルの変更

### 6.2 更新対象ドキュメント

- **[docs/DATABASE.md](../docs/DATABASE.md)**: データベーススキーマ定義
- **[docs/API.md](../docs/API.md)**: API エンドポイント仕様
- **[docs/SETUP.md](../docs/SETUP.md)**: 環境構築手順
- **[docs/ARCHITECTURE.md](../docs/ARCHITECTURE.md)**: システムアーキテクチャ

### 6.3 更新フロー

```bash
# 1. 変更内容を確認し、docs/ 更新が必要か判断
# 2. 必要な場合は新しいブランチを作成
git checkout main
git pull
git checkout -b docs-update-<内容>

# 3. ドキュメントを更新
# 4. コミット・push・PR作成
# 5. code-reviewer サブエージェント レビュー → マージ（通常フロー）
```

---

## 7. Issue作成（必要に応じて）

詳細: [ISSUE_GUIDELINES.md](./ISSUE_GUIDELINES.md)

- レビューでCritical/Major問題が発見された場合
- バグが発見された場合
- 新機能の要望がある場合

---

## 詳細ガイドライン

各工程の詳細は以下のドキュメントを参照してください：

- **[SETUP_AND_MCP.md](./SETUP_AND_MCP.md)**: 環境構築・MCP設定
- **[NAMING_CONVENTIONS.md](./NAMING_CONVENTIONS.md)**: 命名規則
- **[TESTING.md](./TESTING.md)**: テストガイドライン
- **[COMMIT_GUIDELINES.md](./COMMIT_GUIDELINES.md)**: コミットメッセージガイドライン
- **[PR_AND_REVIEW.md](./PR_AND_REVIEW.md)**: PR作成・レビュー・マージプロセス（最重要）
- **[ISSUE_GUIDELINES.md](./ISSUE_GUIDELINES.md)**: Issue作成ガイドライン

---

## 注意事項

- ⚠️ **mainブランチへの直接作業は絶対禁止**
- ⚠️ **コミット前に必ず動作確認とE2Eテストを実施**
- ⚠️ **PR作成直後に必ずcode-reviewer サブエージェント レビューを依頼**
- ⚠️ **Critical問題が存在する場合は絶対にマージしない**
- ⚠️ **PR作成→レビュー→マージまでを1セットの作業として完了させる**（PRを溜めない）
- ⚠️ **マージ後は必ず docs/ の更新が必要か確認する**
- ⚠️ **毎セッション開始時にSerenaメモリから状況を把握する**
