# PR マージプロセス

このドキュメントでは、PRのレビューからマージまでの標準プロセスを定義します。

**最終更新**: 2025-10-01
**更新理由**: Claude Code サブエージェント (Task tool) による実際のレビューフローに合わせて全面改訂

---

## 標準マージフロー

すべてのPRは以下のプロセスに従ってレビュー・マージを実施します。

### 1. PR作成

- ブランチから`main`ブランチへのPRを作成
- PR説明には以下を含める：
  - 変更概要
  - 主な変更内容（箇条書き）
  - テスト結果
  - スクリーンショット（UI変更の場合）
  - 注意事項

**参考**: [PR_GUIDELINES.md](./PR_GUIDELINES.md)

### 2. Claude Code サブエージェント (Task tool) によるレビュー

PRが作成されたら、**Claude Code サブエージェント (Task tool)** を使用してレビューを依頼します。

#### レビュー依頼方法

Task toolを使用して以下のプロンプトで依頼します:

```
Task tool に以下の内容で依頼:
"あなたはコードレビュアーです。以下のPRを詳細にレビューしてください。

# PR情報
- タイトル: [タイトル]
- 説明: [説明文]

# 差分
[git diffの内容]

# レビュー観点
1. セキュリティ
2. コード品質
3. ベストプラクティス
4. API設計
5. UX/UI
6. ドキュメント

# 出力形式
- Critical（致命的）: 🔴
- Major（重要）: 🟠
- Minor（軽微）: 🟡
- 良い点
- 総合評価: マージ可/マージ不可"
```

#### レビュー観点

- **セキュリティ**: 認証・認可、入力検証、SQLインジェクション対策
- **コード品質**: 命名規則、関数分割、DRY原則、エラーハンドリング
- **ベストプラクティス**: フレームワークの推奨パターン、パフォーマンス
- **API設計**: RESTful設計、レスポンス形式の一貫性
- **UX/UI**: 使いやすさ、アクセシビリティ
- **ドキュメント**: README、APIドキュメント、コメント

#### レビュー結果の分類

- **Critical（致命的）** 🔴: データ損失、セキュリティリスク、即座に修正が必要
- **Major（重要）** 🟠: パフォーマンス問題、保守性の大幅低下、マージ前または直後に修正推奨
- **Minor（軽微）** 🟡: コード品質改善、UX向上、今後の改善点として記録

### 3. レビュー結果の評価

Claude Code サブエージェント (Task tool) からのレビュー結果を以下の基準で評価します：

#### マージ可

- **Critical問題がゼロ**
- Major問題が条件付きで許容可能
- バックエンドでのセキュリティ対策が適切

#### マージ不可（要修正）

- **Critical問題が1つ以上存在**
- Major問題が複数あり実害が大きい
- セキュリティリスクが高い

### 4. 修正対応（問題がある場合）

レビューで指摘された問題を修正します。

#### 修正手順

1. **指摘事項を確認**
   - Critical/Major/Minorの分類を確認
   - 優先度に基づいて対応計画を立てる

2. **修正を実施**
   ```bash
   # 修正作業
   git add .
   git commit -m "fix: レビュー指摘事項を修正

   - Critical: データベーススキーマ不一致を修正
   - Major: エラーハンドリングを追加

   🤖 Generated with [Claude Code](https://claude.com/claude-code)

   Co-Authored-By: Claude <noreply@anthropic.com>"
   git push
   ```

3. **再レビュー依頼**
   - PR更新後、再度Claude Code サブエージェント (Task tool) にレビュー依頼
   - すべてのCritical/Major問題が解決されるまで繰り返す

### 5. GitHub Issue作成（必要に応じて）

レビューで指摘された問題のうち、すぐに対応できない項目はIssue化します。

```
mcp__github__create_issue を使用:
- title: "[Critical/Major/Minor] 問題の要約"
- body:
  - 問題概要
  - 発生原因
  - 必須対応（Critical/Majorのみ）
  - 優先度
  - 関連PR
- labels: ["bug", "priority: high/medium/low"]
```

**参考**: [ISSUE_GUIDELINES.md](./ISSUE_GUIDELINES.md)

### 6. マージ実行

#### マージ条件

- ✅ レビュー結果が「マージ可」または「マージ可（条件付き）」
- ✅ **Critical問題がゼロ**
- ✅ バックエンドのセキュリティ対策が適切
- ✅ Major問題がIssue化済み（または修正済み）

#### マージ方法

```bash
# MCP GitHub APIを使用
mcp__github__merge_pull_request
  owner: "ACSshiga"
  repo: "nissei"
  pullNumber: <PR番号>
  merge_method: "squash"  # 推奨
  commit_title: "feat: <変更内容の要約> (#PR番号)"
  commit_message: "
<詳細な変更内容>

主な変更:
- 変更点1
- 変更点2
- 変更点3

レビュー実施済み（Claude Code サブエージェント）: <マージ判定>
- セキュリティ: <評価>
- 今後の改善点: Issue #XX, #YY で管理予定
"
```

### 7. docs/ ディレクトリの更新確認（マージ後必須）

⚠️ **重要**: **PR作成→レビュー→マージまでを1セットの作業として完了させる**
- PRが溜まると干渉したり競合の原因になるため、必ずマージまで完了させる
- マージ後は必ず docs/ の更新が必要か確認する

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

### 8. レビュー履歴の記録

マージ後、`docs/PR_REVIEW_HISTORY.md` を更新します。

#### 記録内容

```markdown
## PR #XX: [タイトル]

**マージ日時**: 2025-10-01
**レビュアー**: Claude Code サブエージェント (Task tool)
**判定**: [マージ可/マージ不可]

### 変更内容
[主要な変更点のリスト]

### レビュー結果

#### 問題点

**Critical（致命的）** 🔴
[致命的な問題のリスト]

**Major（重要）** 🟠
[重要な問題のリスト]

**Minor（軽微）** 🟡
[軽微な問題のリスト]

#### 良い点
[良かった点のリスト]

#### 総合評価
[マージ可否の判断理由]

### 今後のアクションアイテム

**Priority: High（優先度：高）**
- [ ] Issue #XX: Critical問題の修正

**Priority: Medium（優先度：中）**
- [ ] Issue #YY: Major問題の修正

**Priority: Low（優先度：低）**
- [ ] Issue #ZZ: Minor問題の修正

### マージ詳細
- **マージコミット**: [commit SHA]
- **マージ方法**: squash merge
- **ブランチ**: [branch名] → main
```

---

## 実施例

### PR #22: 管理者パネルと工数入力の改善

1. **PR作成**: feat-admin-panel-and-worklog-improvements → main
2. **Claude Code サブエージェント (Task tool) レビュー**: マージ可（条件付き）
   - Major問題3件（JWT改ざん対策、URL推測、エラーハンドリング）
   - Minor問題5件
3. **評価**: バックエンドで適切に保護されており、実害は限定的と判断
4. **マージ**: squash mergeで実行（コミット: 29d8b066）
5. **記録**: `docs/PR_REVIEW_HISTORY.md` に詳細を記録
6. **アクションアイテム**: 今後のIssueとして8件を整理

### PR #21, #20: マージ不可（Critical問題あり）

1. **PR作成**: 工数入力機能の改修
2. **Claude Code サブエージェント (Task tool) レビュー**: マージ不可
   - **Critical問題**: データベーススキーマ不一致によるデータ損失
3. **Issue作成**: Issue #23, #24 を作成
4. **対応**: Issue修正後に再レビュー → マージ

---

## 注意事項

- ⚠️ **Critical問題が存在する場合は絶対にマージしない**
- ⚠️ **セキュリティリスクが高い場合は追加レビューを実施**
- ⚠️ **Major問題は必ずIssue化またはマージ前に修正**
- ⚠️ **レビュー履歴は必ず `docs/PR_REVIEW_HISTORY.md` に記録**

---

## 参考資料

- [COMMIT_GUIDELINES.md](./COMMIT_GUIDELINES.md): コミットメッセージガイドライン
- [PR_GUIDELINES.md](./PR_GUIDELINES.md): PR作成ガイドライン
- [CODE_REVIEW.md](./CODE_REVIEW.md): コードレビューチェックリスト
- [ISSUE_GUIDELINES.md](./ISSUE_GUIDELINES.md): Issue作成ガイドライン
- [MCP_USAGE.md](./MCP_USAGE.md): MCP サーバー運用ガイド
- [../docs/PR_REVIEW_HISTORY.md](../docs/PR_REVIEW_HISTORY.md): 過去のレビュー履歴
