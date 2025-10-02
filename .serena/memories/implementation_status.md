# 実装状況

**最終更新**: 2025-10-02
**プロジェクト**: Nissei 工数管理システム

---

## 📊 全体進捗

### Phase 1: 基本機能（~80%完了）

| 機能カテゴリ | 実装状況 | 備考 |
|------------|---------|------|
| 認証システム | ✅ 100% | Supabase Auth統合完了 |
| ユーザー管理 | ✅ 100% | 管理者パネル実装済み |
| 案件管理（CRUD） | ✅ 80% | 基本機能完了、詳細機能は未実装 |
| 工数入力 | ✅ 90% | スプレッドシート風UI実装済み |
| マスタ管理 | ✅ 100% | 6種類すべて実装済み |
| 請求書生成 | ❌ 0% | 未着手 |
| 資料管理 | ❌ 0% | 未着手 |
| 注意点管理 | ❌ 0% | 未着手 |

---

## ✅ 完了済み機能

### 1. 認証システム（Supabase Auth）

**実装済み**:
- ✅ ユーザー登録（POST /api/auth/register）
- ✅ ログイン（POST /api/auth/login）
- ✅ JWT認証ミドルウェア
- ✅ トークンリフレッシュ
- ✅ ログアウト

**ファイル**:
- `backend/app/api/auth.py`
- `backend/app/core/security.py`
- `frontend/src/app/login/page.tsx`
- `frontend/src/app/register/page.tsx`

---

### 2. ユーザー管理・管理者パネル

**実装済み**:
- ✅ 管理者パネルUI（/admin-panel-secret）
- ✅ ユーザー一覧取得（GET /api/admin/users）
- ✅ ユーザー削除（DELETE /api/admin/users/{id}）
- ✅ ユーザー有効化/無効化（PATCH /api/admin/users/{id}/activate）
- ✅ is_admin権限チェック（require_admin依存関数）

**ファイル**:
- `backend/app/api/admin.py`
- `frontend/src/app/admin-panel-secret/page.tsx`

**完了PR**:
- #22: 管理者パネルと工数入力の改善

---

### 3. 案件管理（Projects）

**実装済み**:
- ✅ 案件一覧取得（GET /api/projects）
  - 検索・フィルタ機能（management_no, machine_no, model, assignee_id, progress_id等）
  - ページネーション対応
- ✅ 案件詳細取得（GET /api/projects/{id}）
- ✅ 案件作成（POST /api/projects）
- ✅ 案件更新（PATCH /api/projects/{id}）
- ✅ 案件削除（DELETE /api/projects/{id}）
- ✅ 自分の担当案件（GET /api/projects/my）

**実装済みフィールド**:
- management_no, machine_no, model, spec_code, full_model_name
- work_category_id, delivery_destination_id, assignee_id, progress_id
- planned_hours, deadline, started_at, completed_at
- reference_code, circuit_diagram_no, delay_reason, notes

**未実装機能**:
- ❌ PDF取り込み（委託書解析）
- ❌ プロジェクト実績工数の自動集計（work_logsとの連携）
- ❌ 進捗自動更新ロジック

**ファイル**:
- `backend/app/api/projects.py`
- `backend/app/models/project.py`
- `backend/app/schemas/project.py`
- `frontend/src/app/projects/page.tsx`
- `frontend/src/app/projects/[id]/page.tsx`
- `frontend/src/app/projects/new/page.tsx`
- `frontend/src/app/projects/[id]/edit/page.tsx`

---

### 4. 工数入力（Work Logs）

**実装済み**:
- ✅ スプレッドシート風グリッドUI
- ✅ 複数行一括入力
- ✅ 工数作成（POST /api/worklogs）
- ✅ 工数更新（PUT /api/worklogs/{id}）
- ✅ 工数削除（DELETE /api/worklogs/{id}）
- ✅ 開始時刻・終了時刻フィールド（start_time, end_time）
- ✅ 作業内容フィールド（work_content）
- ✅ 15分刻みセレクトボックス（15分～8時間）

**未実装機能**:
- ❌ 月グリッドAPI（GET /api/worklogs/grid?month=YYYY-MM）
- ❌ 差分パッチ更新（PUT /api/worklogs/grid）
- ❌ プロジェクトactual_hours自動更新ロジック

**完了PR**:
- #21: 工数入力画面をスプレッドシート風UIに全面改修
- #31: work_logsテーブルに必須カラム追加
- #32: start_time/end_timeフィールド追加

**ファイル**:
- `backend/app/api/worklogs.py`
- `backend/app/models/worklog.py`
- `backend/app/schemas/worklog.py`
- `frontend/src/app/worklogs/page.tsx`
- `frontend/src/app/worklogs/[id]/edit/page.tsx`

---

### 5. マスタ管理（Masters）

**実装済み**（6種類すべて）:
- ✅ 作業区分マスタ（master_work_category）
  - GET/POST/PUT/DELETE /api/masters/work-category
- ✅ 機種マスタ（master_kishyu）
  - GET/POST/PUT/DELETE /api/masters/kishyu
- ✅ 納入先マスタ（master_nounyusaki）
  - GET/POST/PUT/DELETE /api/masters/nounyusaki
- ✅ 進捗マスタ（master_shinchoku）
  - GET/POST/PUT/DELETE /api/masters/shinchoku
- ✅ 注意点カテゴリマスタ（master_chuiten_category）
  - GET/POST/PUT/DELETE /api/masters/chuiten-category
- ✅ 注意点マスタ（master_chuiten）
  - GET/POST/PUT/DELETE /api/masters/chuiten

**UI実装状況**:
- ✅ `/masters/sagyou-kubun` - 作業区分マスタ
- ✅ `/masters/machine-series` - 機種マスタ
- ✅ `/masters/shinchoku` - 進捗マスタ
- ✅ `/masters/toiawase` - 納入先マスタ（名前は「問い合わせ」だが実体は納入先）
- ⚠️ 注意点カテゴリ・注意点マスタのUI未実装

**ファイル**:
- `backend/app/api/masters.py`
- `backend/app/models/master.py`
- `backend/app/schemas/master.py`
- `frontend/src/app/masters/page.tsx`
- `frontend/src/app/masters/sagyou-kubun/page.tsx`
- `frontend/src/app/masters/machine-series/page.tsx`
- `frontend/src/app/masters/shinchoku/page.tsx`
- `frontend/src/app/masters/toiawase/page.tsx`

---

## ❌ 未実装機能

### 1. 請求書生成（Invoices）

**未実装**:
- ❌ 請求プレビューAPI（GET /api/invoices?month=YYYY-MM）
- ❌ 請求締め確定API（POST /api/invoices/close）
- ❌ CSV出力API（GET /api/invoices/export?month=YYYY-MM）
- ❌ invoicesテーブル
- ❌ invoice_itemsテーブル
- ❌ 請求書画面UI

**必要な作業**:
1. テーブル作成（invoices, invoice_items）
2. API実装（preview, close, export）
3. CSV生成ロジック
4. フロントエンドUI実装

---

### 2. 資料管理（Materials）

**未実装**:
- ❌ materialsテーブル
- ❌ Supabase Storage / MinIO設定
- ❌ 資料一覧API（GET /api/materials）
- ❌ 資料アップロードAPI（POST /api/materials）
- ❌ 資料削除API（DELETE /api/materials/{id}）
- ❌ スコープベース検索ロジック
- ❌ 資料管理画面UI

**必要な作業**:
1. materialsテーブル作成
2. Supabase Storageバケット設定
3. ファイルアップロード・ダウンロードAPI実装
4. スコープ階層検索ロジック実装
5. フロントエンドUI実装

---

### 3. 注意点管理（Chuiten）

**未実装**:
- ❌ chuiten（注意点インスタンス）テーブル
- ✅ master_chuiten_category（カテゴリマスタ）- バックエンドAPI完了、UI未実装
- ✅ master_chuiten（注意点マスタ）- バックエンドAPI完了、UI未実装
- ❌ 案件別注意点API（GET/POST /api/projects/{id}/chuiten）
- ❌ 注意点チェックAPI（PUT /api/projects/{id}/chuiten/{itemId}）
- ❌ 注意点管理画面UI

**必要な作業**:
1. chuitenテーブル作成
2. 案件別注意点API実装
3. マスタ展開ロジック実装
4. フロントエンドUI実装

---

## 🚨 既知の問題

### 1. Supabaseスキーマキャッシュ問題（ブロッカー）

**状況**:
- バックエンドのSupabaseクライアントが `work_logs` テーブルを認識しない
- エラー: `"Could not find the table 'public.work_logs' in the schema cache"`
- Supabase MCP（別接続）では `work_logs` テーブルを正しく認識

**試した解決策**:
- ✅ マイグレーション適用（backend/migrations/2025-10-02_create_all_tables.sql）
- ✅ バックエンドコンテナ再起動（複数回）
- ✅ 全コンテナ再起動
- ❌ スキーマキャッシュのリフレッシュ（Supabase側の操作が必要）

**影響**:
- 工数入力画面のE2Eテストが中断中
- 現時点で完了した作業:
  - ✅ データベースリセット完了
  - ✅ ログイン機能テスト成功
  - ✅ UI経由でのプロジェクト作成成功

**解決方法**:
- Option A: Supabase Studioでスキーマをリフレッシュ（推奨）
- Option B: E2Eテストをスキップして、コードレベル検証に切り替え

---

### 2. 仕様の齟齬（要件定義 vs 実装）

**状況**:
- 要件定義書: シンプルな案件管理
- 実装: 製造業専門仕様（管理No、機番、機種、トン数、マスタ連携等）

**未確認事項**（5項目）:
1. 案件管理画面の必要項目
2. PDF取り込み方法（自動/手動）
3. 担当者管理（1案件に複数？）
4. 進捗管理の仕様
5. 工数入力の粒度

**次のアクション**:
- ユーザーに上記5項目について確認
- 確認後、要件定義書を更新 or 実装を修正

---

### 3. データ整合性の問題（修正済み）

**過去の問題**:
- Issue #23: データベーススキーマ不一致（start_time, end_time, work_contentがコメントアウト）→ **修正完了**
- Issue #24: プロジェクト変更時の実績工数調整ロジック不足 → **修正完了**
- Issue #27: usersテーブルのpasswordカラム名不一致 → **修正完了**

---

## 📋 次のステップ

### 優先度: High（最優先）

1. **仕様確認ミーティング**
   - 未確認事項5項目の確認
   - 要件定義書の更新 or 実装の修正決定

2. **Supabaseスキーマキャッシュ問題の解決**
   - Supabase Studioでスキーマをリフレッシュ
   - または、コードレベル検証に切り替え

### 優先度: Medium

3. **請求書生成機能の実装**
   - invoices, invoice_itemsテーブル作成
   - API実装（preview, close, export）
   - CSV生成ロジック
   - フロントエンドUI実装

4. **資料管理機能の実装**
   - materialsテーブル作成
   - Supabase Storage設定
   - スコープベース検索ロジック
   - フロントエンドUI実装

5. **注意点管理機能の実装**
   - chuitenテーブル作成
   - 案件別注意点API実装
   - マスタ展開ロジック
   - フロントエンドUI実装

### 優先度: Low

6. **E2Eテスト整備**
   - Playwright MCPツールを使用
   - 全機能のテストシナリオ作成

7. **パフォーマンス最適化**
   - N+1クエリの解消
   - キャッシング導入（Redis検討）
   - フロントエンドコード分割

---

## 🔧 技術的負債

### 1. テストカバレッジ不足
- バックエンド: 単体テスト未実装
- フロントエンド: 単体テスト未実装
- E2E: 一部のみ実装

### 2. エラーハンドリング不足
- Supabase APIエラーハンドリング（一部修正済み）
- フロントエンド通信エラーの詳細表示

### 3. バリデーション不足
- 15分刻みバリデーションがフロントエンドのみ
- バックエンド側のバリデーション強化が必要

### 4. UI/UX改善
- `alert()`の使用（トースト通知推奨）
- プロジェクト選択肢がIDのみ表示（プロジェクト名表示推奨）
- ローディング状態表示の統一

---

## 📝 最近のPR・マージ履歴

- #33: usersテーブルのpasswordカラム名をhashed_passwordに統一
- #32: 工数入力APIにstart_time/end_timeフィールドを追加
- #31: Supabaseマイグレーションでwork_logsテーブルに必須カラムを追加
- #21: 工数入力画面をスプレッドシート風UIに全面改修
- #22: 管理者パネルと工数入力の改善

---

## 関連ドキュメント

- データベース仕様: `.serena/memories/database_specifications.md`
- API仕様: `.serena/memories/api_specifications.md`
- システムアーキテクチャ: `.serena/memories/system_architecture.md`
- 現在の課題: `.serena/memories/current_issues_and_priorities.md`
