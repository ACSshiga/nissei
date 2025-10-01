# 開発ワークフロー

## 作業開始時（必須）

### ブランチ作成
- **必ず専用ブランチを作成する**
  - `feat-<機能名>`: 新機能追加
  - `fix-<修正内容>`: バグ修正
  - `refactor-<対象>`: リファクタリング
  - `docs-<内容>`: ドキュメント更新

- **mainブランチでの直接作業は絶対禁止**
  - いかなる変更もmainブランチに直接コミットしない

## 作業中

### 慎重な修正
- 該当修正によって他の処理に問題がないか確認
- 他の動作に影響がある場合は既存の期待動作が正常に動作するよう修正

### コミット前の確認（必須）
- **必ず動作確認を行う**
  - 動作確認中にエラーが発見された際はタスクを更新
  - エラーがない状態でコミット
- **E2Eテストを実施**
  - PlaywrightのMCPツールを使用
  - ユーザー目線での動作を確認

## 作業終了時（必須）

### 1. 変更をコミット
```bash
git add .
git commit -m "feat: 機能の説明

詳細な変更内容

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

### 2. リモートブランチにpush
```bash
git push -u origin <ブランチ名>
```

### 3. PR作成
- MCP GitHub APIを使用してPR作成
- タイトル: 簡潔な変更内容
- 本文: 概要、変更内容、テスト手順を記載

### 4. レビュー依頼（必須）
⚠️ **重要**: PR作成直後に必ず実施

**推奨方法：Task tool（general-purposeサブエージェント）**

```typescript
Task tool を使用:
- subagent_type: "general-purpose"
- prompt: "Please review PR#{番号} in repository {owner}/{repo}.
           Check all files and verify that all issues are resolved.
           Return either 'All issues resolved, ready to merge' or list remaining problems."
```

- サブエージェントが最新コミットを自動確認
- 指摘事項を確認し、必要に応じて修正

### 5. 修正が必要な場合
レビューからの指摘事項がある場合：

1. **指摘事項を確認**
   - サブエージェントのレビュー結果を確認
   - 各指摘の優先度を確認

2. **修正を実施**
   - 指摘された箇所を修正
   - コミット・push
   ```bash
   git add .
   git commit -m "fix: レビュー指摘事項を修正

   - 指摘1の修正内容
   - 指摘2の修正内容

   🤖 Generated with [Claude Code](https://claude.com/claude-code)

   Co-Authored-By: Claude <noreply@anthropic.com>"
   git push
   ```

3. **再度レビュー依頼**
   - PRを更新するたびに Task tool で再レビューを依頼
   - 修正内容をコメントで報告（推奨）

4. **修正完了まで繰り返し**
   - すべての指摘が解決されるまで「修正 → push → Task toolレビュー依頼」を繰り返す

### 6. レビュー承認後にマージ
レビューが承認されたら：

1. **PR状態を確認**
   - `mcp__github__get_pull_request` でPR状態を確認
   - `mergeable: true` であることを確認

2. **mainブランチへマージ**
   ```bash
   # MCP GitHub APIを使用
   mcp__github__merge_pull_request
   ```
   - merge_method: `squash` または `merge` （プロジェクト規約に従う）
   - コミットメッセージを確認

3. **ブランチ削除（任意）**
   - マージ後、不要になったブランチを削除可能
   ```bash
   git branch -d <ブランチ名>
   git push origin --delete <ブランチ名>
   ```

## 詳細ガイドライン

- コミット規約: [COMMIT_GUIDELINES.md](./COMMIT_GUIDELINES.md)
- PR作成ルール: [PR_GUIDELINES.md](./PR_GUIDELINES.md)
- コードレビュー: [CODE_REVIEW.md](./CODE_REVIEW.md)
