# データベース設計

## データベース構成

- **プラットフォーム**: Supabase (PostgreSQL)
- **プロジェクトID**: wwyrthkizkcgndyorcww
- **ストレージ**: Supabase Storage (本番), MinIO (開発)

## テーブル一覧（12テーブル）

### コアテーブル
1. **users** - ユーザー管理
2. **projects** - 案件管理
3. **worklogs** - 工数入力（旧名: work_logs）
4. **materials** - 資料管理
5. **invoices** - 請求書
6. **invoice_items** - 請求書明細

### マスタテーブル
7. **master_work_category** - 作業区分（盤配/線加工）
8. **master_kishyu** - 機種マスタ
9. **master_nounyusaki** - 納入先マスタ
10. **master_shinchoku** - 進捗マスタ
11. **master_chuiten_category** - 注意点カテゴリ
12. **master_chuiten** - 注意点マスタ

## 主要テーブル

### projects（案件）

```
management_no   - 管理番号（E252019等、ユニーク）
machine_no      - 機番（HMX7-CN2等）
model           - 機種（NEX140Ⅲ）
spec_code       - 仕様コード（24AK）
full_model_name - フルモデル名（NEX140Ⅲ-24AK）
assignee_id     - 担当者
progress_id     - 進捗
planned_hours   - 予定工数
deadline        - 作図期限
```

**機種名の構造**:
- `model`: シリーズ + トン数 + 世代（例: NEX140Ⅲ）
- `spec_code`: 仕様コード（例: 24AK）
- `full_model_name`: model + "-" + spec_code（例: NEX140Ⅲ-24AK）

### worklogs（工数）

```
project_id       - 案件ID
user_id          - ユーザーID
work_date        - 作業日
duration_minutes - 作業時間（分）※15分単位
start_time       - 開始時刻（オプション）
end_time         - 終了時刻（オプション）
work_content     - 作業内容（オプション）
```

### invoices（請求書）

```
invoice_number   - 請求書番号（INV-YYYYMM-XXX形式、UNIQUE）
issue_date       - 発行日
total_amount     - 合計工数（Decimal 12,2）
status           - ステータス（draft/sent/paid）
```

### invoice_items（請求書明細）

```
invoice_id       - 請求書ID（外部キー）
management_no    - 管理番号（プロジェクトから）
machine_no       - 機番（プロジェクトから）
actual_hours     - 実工数（Decimal 8,2）
sort_order       - ソート順
```

### materials（資料）

4段階スコープ（machine/model/tonnage/series）で資料を共有。

```
title       - 資料タイトル
scope       - 共有スコープ（machine/model/tonnage/series）
series      - シリーズ（NEX）
tonnage     - トン数（140）
file_path   - ファイルパス（Supabase Storage）
```

**スコープ階層**:
1. `machine`: 特定機番専用（例: HMX7-CN2専用）
2. `model`: 特定機種専用（例: NEX140Ⅲ-24AK専用）
3. `tonnage`: トン数共通（例: 140トン全機種）
4. `series`: シリーズ共通（例: NEXシリーズ全体）

## マイグレーション

### Supabase CLIを使用

```bash
# マイグレーション作成
supabase migration new migration_name

# ローカル適用
supabase db reset

# 本番適用
supabase db push
```

### マイグレーション順序

```
1. users
2. マスタテーブル（6種類）
3. projects
4. worklogs（work_logsからリネーム）
5. materials
6. invoices, invoice_items
7. projects (management_no, machine_no追加)
8. create_invoice_with_items() ストアドプロシージャ
```

## 詳細仕様

AI用の詳細なデータベース仕様は `.serena/memories/database_specifications.md` を参照。
