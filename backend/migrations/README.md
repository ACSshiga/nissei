# Supabase マイグレーション履歴

このディレクトリには、Supabaseデータベースに適用したマイグレーションの記録を保存します。

## マイグレーション一覧

### 2025-10-02 (1): 初期テーブル作成（Issue #23対応）

**マイグレーション名**: `create_all_tables_with_worklogs_columns`
**ファイル**: `2025-10-02_create_all_tables.sql`
**適用日時**: 2025-10-02 10:30 JST
**適用者**: Supabase MCP
**ステータス**: ✅ 適用済み

**目的**: Issue #23（データ損失問題）の解決
- `work_logs`テーブルに`start_time`, `end_time`, `work_content`カラムを追加
- その他すべての必要なテーブルを作成

**作成されたテーブル**:
- `users` (既存)
- `projects` (estimated_hours, actual_hoursカラム含む)
- `work_logs` ← **Issue #23対応: start_time, end_time, work_content含む**
- `material_categories`
- `work_types`
- `materials`
- `invoices`
- `checklists`

**適用コマンド**:
```
Supabase MCP: mcp__supabase__apply_migration
```

**関連Issue**: #23, #24

---

### 2025-10-02 (2): projectsテーブルにmanagement_noカラム追加

**マイグレーション名**: `add_management_no_to_projects`
**適用日時**: 2025-10-02 11:00 JST
**適用者**: Supabase MCP
**ステータス**: ✅ 適用済み

**目的**: バックエンドコードがmanagement_noを参照しているため追加

**変更内容**:
```sql
ALTER TABLE projects ADD COLUMN management_no VARCHAR(50) UNIQUE;
CREATE INDEX idx_projects_management_no ON projects(management_no);
```

**適用コマンド**:
```
Supabase MCP: mcp__supabase__apply_migration
```

---

## マイグレーション戦略

### 既存環境（本番・開発共通）
1. すべてのマイグレーションは既に適用済み
2. テーブル名は`work_logs`（アンダースコア付き）で統一
3. バックエンドコードも`work_logs`を使用するよう修正済み

### 新規環境セットアップ
```bash
# Supabase MCPを使用して全マイグレーション実行
mcp__supabase__apply_migration(2025-10-02_create_all_tables.sql)
mcp__supabase__apply_migration(add_management_no_to_projects)
```

## ロールバック手順

基本的にロールバックは推奨されません。必要な場合は以下を実行：

```sql
-- projects.management_noカラム削除
ALTER TABLE projects DROP COLUMN IF EXISTS management_no;

-- すべてのテーブル削除（注意: データも削除されます）
DROP TABLE IF EXISTS checklists CASCADE;
DROP TABLE IF EXISTS invoices CASCADE;
DROP TABLE IF EXISTS materials CASCADE;
DROP TABLE IF EXISTS work_logs CASCADE;
DROP TABLE IF EXISTS projects CASCADE;
DROP TABLE IF EXISTS material_categories CASCADE;
DROP TABLE IF EXISTS work_types CASCADE;
```

## 備考
- バックエンドコードは3カラム（start_time, end_time, work_content）に既に対応済み
- フロントエンドコードも3カラムを送信済み
- 問題はデータベース側にカラムが存在しなかったこと
- 今回のマイグレーションでIssue #23のデータ損失問題が解決
