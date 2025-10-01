# Pull Requestガイドライン

## PR作成時の必須項目

### タイトル
- 簡潔に変更内容を記述
- コミットメッセージのsubjectと同じ形式
- 例: `ユーザーダッシュボード画面を追加`

### 本文構成

```markdown
## 概要
この変更の目的を簡潔に説明

## 変更内容
- 具体的な変更点1
- 具体的な変更点2
- 具体的な変更点3

## テスト手順
1. 手順1
2. 手順2
3. 期待される結果

## 関連Issue
Closes #123
```

## PR作成後の必須アクション

### 1. レビュー依頼（必須）

⚠️ **PR作成直後に必ず実施**

**推奨方法：Task tool（general-purposeサブエージェント）**

Claude Code内蔵のサブエージェントを使用してレビューを実施します。

```typescript
Task tool を使用:
- subagent_type: "general-purpose"
- prompt: "Please review PR#{番号} in repository {owner}/{repo}.
           Check all files and verify that all issues are resolved.
           Return either 'All issues resolved, ready to merge' or list remaining problems."
```

**レビュー結果の確認**:
- サブエージェントが最新コミットを自動確認
- 修正済み項目・未解決項目をレポート
- 「All issues resolved, ready to merge」ならマージ可能

### 2. レビュー対応（修正が必要な場合）

#### 修正の実施
1. **指摘箇所を修正**
2. **コミット・push**
   ```bash
   git add .
   git commit -m "fix: レビュー指摘事項を修正

   - 指摘1の修正内容
   - 指摘2の修正内容

   🤖 Generated with [Claude Code](https://claude.com/claude-code)

   Co-Authored-By: Claude <noreply@anthropic.com>"
   git push
   ```

#### 再レビュー依頼（必須）
⚠️ **PRを更新するたびに必ず実施**

- Task toolで再度レビュー依頼を実施
- 修正内容を報告（推奨）:
  ```markdown
  ## ✅ レビュー指摘事項を修正しました

  ### 修正内容
  - 修正1: 具体的な内容
  - 修正2: 具体的な内容

  修正コミット: <commit-hash>
  ```

#### 修正完了まで繰り返し
- すべての指摘が解決されるまで「修正 → push → Task toolレビュー」を繰り返す

### 3. マージ（レビュー承認後）

#### マージ前の確認
```bash
# PR状態を確認
mcp__github__get_pull_request

# 確認項目:
# - mergeable: true
# - レビューが承認済み
# - すべての指摘事項が解決済み
```

#### mainブランチへマージ
```bash
# MCP GitHub APIを使用
mcp__github__merge_pull_request
```

- **merge_method**: `squash`（推奨）または `merge`
- コミットメッセージを確認
- Discord通知が自動送信される

#### マージ後のクリーンアップ（任意）
```bash
# ローカルブランチ削除
git branch -d <ブランチ名>

# リモートブランチ削除
git push origin --delete <ブランチ名>
```

## PRの種類別テンプレート

### 新機能追加

```markdown
## 概要
[機能名]を追加しました。

## 変更内容
- 機能の実装内容
- 関連するファイルの変更
- データベーススキーマの変更（あれば）

## テスト手順
1. [環境/画面]にアクセス
2. [操作手順]
3. [期待される動作]

## スクリーンショット
（あれば添付）

## 関連Issue
Closes #XXX
```

### バグ修正

```markdown
## 概要
[バグの内容]を修正しました。

## 問題
- 発生していた問題の詳細
- 再現手順

## 原因
- 問題の根本原因

## 修正内容
- 具体的な修正内容

## テスト手順
1. 以前のバグ再現手順を実施
2. バグが解消されていることを確認

## 関連Issue
Fixes #XXX
```

### リファクタリング

```markdown
## 概要
[対象]をリファクタリングしました。

## 目的
- リファクタリングの理由
- 改善される点

## 変更内容
- 具体的な変更内容
- 動作に変更がないこと

## テスト手順
1. 既存機能が正常に動作することを確認
2. E2Eテストがすべてパス

## 関連Issue
なし
```

## チェックリスト

PR作成前に以下を確認：

- [ ] 専用ブランチで作業している
- [ ] 動作確認が完了している
- [ ] E2Eテストを実施済み
- [ ] コミットメッセージが規約に準拠
- [ ] PRテンプレートに従って記載
- [ ] 関連Issueがあればリンク
- [ ] Task toolレビュー依頼を実施予定
