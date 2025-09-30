# Nissei 工数管理システム 要件定義書 v1.0

**作成日**: 2025-09-30
**最終更新**: 2025-09-30
**プロジェクト**: 既存Google Spreadsheet + Apps ScriptシステムのWeb化

---

## 📋 プロジェクト概要

### 目的
既存のGoogle Spreadsheet + Apps Scriptベースの工数管理システムを、**FastAPI + Next.jsによるWebアプリケーション**に完全移行し、以下を実現する：

1. **業務の効率化**: データ同期の完全自動化により、二重入力や転記作業を撲滅
2. **正確性の向上**: 手作業を排除し、ヒューマンエラーのない正確なデータ管理
3. **情報共有の円滑化**: 各担当者が必要な情報に、他のメンバーを気にせずアクセス可能
4. **モバイル対応**: スマートフォンからも工数入力可能

### 対象業務
- 設計業務の進捗管理
- 工数入力・集計（15分刻み、案件ごと）
- 委託書PDFからの自動データ取り込み
- 請求書データ生成（Excel出力）
- 資料管理（機種・機番別）
- 資料作成注意点のチェックリスト管理

### 対象ユーザー
- **社内の設計者のみ**（外注なし）
- 全員が全案件を閲覧可能（ロール分けなし）
- 請求確定操作のみ限定権限を検討

---

## 🔐 認証要件

### 認証方式
- **独自認証**（メール + パスワード、8文字以上）
- **Google連携は不要**
- デバイス記憶機能
- 将来的に2段階認証追加可能な設計

### ユーザー属性
```sql
User:
  - id (UUID)
  - email (unique)
  - username
  - hashed_password
  - role (worker/admin) -- 請求確定権限用
  - color (担当者色分け用)
  - is_active
  - created_at
  - updated_at
```

---

## 🗂️ データモデル設計

### ER図（概要）

```
User (ユーザー)
  ├─→ Project (案件) [担当者]
  ├─→ WorkLog (工数入力) [多]
  └─→ Material (資料) [登録者]

Project (案件)
  ├─→ WorkLog (工数入力) [多]
  ├─→ Material (資料) [多]
  ├─→ ProjectChecklistItem (注意点チェック) [多]
  ├─→ MasterSagyouKubun (作業区分)
  ├─→ MasterShinchoku (進捗)
  └─→ MasterToiawase (問い合わせ)

Invoice (請求書)
  └─→ Project (案件) [多] （完了日による月次抽出）
```

### 主要テーブル定義

#### projects（案件）
```sql
-- 既存項目
- id: UUID PRIMARY KEY
- user_id: UUID FOREIGN KEY -- 担当者
- management_no: VARCHAR UNIQUE NOT NULL -- 管理No（E25A001形式）
- machine_no: VARCHAR -- 機番
- series: VARCHAR -- 機種（シリーズ名）
- status: VARCHAR -- 進捗ステータス
- estimated_hours: INTEGER -- 予定工数（分）
- actual_hours: INTEGER -- 実績工数（分、自動集計）
- start_date: DATE -- 仕掛日
- created_at: TIMESTAMP
- updated_at: TIMESTAMP

-- 追加項目（既存シートとの整合性）
- sagyou_kubun: VARCHAR -- 作業区分（盤配/線加工/委託）
- machine_url: VARCHAR -- 機番リンク（資料集URL）
- std_material_url: VARCHAR -- STD資料リンク（資料集URL）
- reference_kiban: VARCHAR -- 参考製番
- circuit_diagram_no: VARCHAR -- 回路図番
- toiawase_status: VARCHAR -- 問い合わせステータス
- temp_code: VARCHAR -- 仮コード
- destination: VARCHAR -- 納入先
- complete_date: DATE -- 完了日
- drawing_deadline: DATE -- 作図期限
- progress_editor: VARCHAR -- 進捗記入者（自動記録）
- overrun_reason: TEXT -- 係り超過理由
- notes: TEXT -- 注意点
- remarks: TEXT -- 備考
- source_pdf_id: UUID -- インポート元PDF
```

#### work_logs（工数入力）
```sql
- id: UUID PRIMARY KEY
- user_id: UUID FOREIGN KEY
- project_id: UUID FOREIGN KEY
- work_date: DATE NOT NULL
- start_time: TIME
- end_time: TIME
- duration_minutes: INTEGER NOT NULL -- 15分刻み
- sagyou_kubun: VARCHAR -- 作業区分
- work_content: TEXT -- 作業内容メモ
- created_at: TIMESTAMP
- updated_at: TIMESTAMP

INDEX: (project_id, work_date)
INDEX: (user_id, work_date)
```

#### materials（資料）
```sql
- id: UUID PRIMARY KEY
- scope: VARCHAR NOT NULL -- 'model' (機種) or 'machine' (機番)
- key_value: VARCHAR NOT NULL -- 機種名 or 機番
- title: VARCHAR NOT NULL
- kind: VARCHAR NOT NULL -- 'link' (URL) or 'file' (アップロード)
- url_or_storage_ref: VARCHAR NOT NULL
- description: TEXT
- tags: TEXT[] -- 検索用タグ
- uploaded_by: UUID FOREIGN KEY
- created_at: TIMESTAMP
- updated_at: TIMESTAMP

INDEX: (scope, key_value)
UNIQUE: (scope, key_value, title)
```

#### checklist_templates（注意点マスタ）
```sql
- id: UUID PRIMARY KEY
- category: VARCHAR NOT NULL -- 機種カテゴリ（H0, NEX, B板など）
- item_key: VARCHAR NOT NULL -- 内部キー
- title: VARCHAR NOT NULL -- 表示名
- detail: TEXT -- 補足説明
- severity: VARCHAR DEFAULT 'recommended' -- 'required' or 'recommended'
- default_assignee_role: VARCHAR
- autocomplete_hint: TEXT -- 自動入力ヒント
- sort_order: INTEGER
- created_at: TIMESTAMP

INDEX: (category)
```

#### project_checklist_items（案件別チェック項目）
```sql
- id: UUID PRIMARY KEY
- project_id: UUID FOREIGN KEY
- template_id: UUID FOREIGN KEY (nullable) -- テンプレート由来の場合
- category: VARCHAR
- item_key: VARCHAR
- title: VARCHAR NOT NULL
- detail: TEXT
- severity: VARCHAR
- assignee_user_id: UUID FOREIGN KEY (nullable)
- status: VARCHAR DEFAULT 'open' -- 'open' or 'done'
- completed_at: TIMESTAMP
- completed_by: UUID FOREIGN KEY
- notes: TEXT
- created_at: TIMESTAMP

INDEX: (project_id, status)
```

#### invoices（請求書）
```sql
- id: UUID PRIMARY KEY
- invoice_month: DATE NOT NULL -- 請求月（YYYY-MM-01形式）
- total_hours_decimal: DECIMAL(10,2) -- 合計工数（小数時間）
- total_amount: DECIMAL(12,2) -- 合計金額
- hourly_rate: DECIMAL(10,2) DEFAULT 4500 -- 時間単価
- status: VARCHAR DEFAULT 'draft' -- 'draft' / 'closed'
- closed_by: UUID FOREIGN KEY
- closed_at: TIMESTAMP
- created_at: TIMESTAMP

UNIQUE: (invoice_month)
```

#### invoice_items（請求書明細）
```sql
- id: UUID PRIMARY KEY
- invoice_id: UUID FOREIGN KEY
- project_id: UUID FOREIGN KEY
- management_no: VARCHAR -- 管理No
- work_content: VARCHAR -- 業務委託内容（機番）
- actual_hours_decimal: DECIMAL(10,2) -- 実工数（小数時間）
- created_at: TIMESTAMP
```

#### マスタテーブル（簡略版）

```sql
-- 進捗マスタ
master_shinchoku:
  - id, status_name, background_color, completion_trigger, start_date_trigger, sort_order

-- 作業区分マスタ
master_sagyou_kubun:
  - id, kubun_name, background_color, sort_order

-- 問い合わせマスタ
master_toiawase:
  - id, status_name, background_color, sort_order

-- PDFインポートログ
pdf_import_logs:
  - id, file_name, file_size, import_status, imported_count, error_message, processed_at
```

---

## 🎯 機能要件

### 1. 案件管理

#### 1.1 PDF自動取り込み（最重要）
- **入力**: 委託書PDF（複数アップロード可）
- **処理**:
  - OCR（Tesseract + 定型座標抽出）
  - 管理No, 機種, 機番, 納入先, 予定工数, 作図期限を自動抽出
  - 作業区分の自動判定（盤配/線加工）
- **出力**:
  - 確認テーブルで一括プレビュー
  - 失敗行は赤表示 + 手修正可能
  - 確定で案件一括登録
- **重複チェック**: 管理Noで既存案件を検出

#### 1.2 案件一覧・検索
- **フィルタ**:
  - 管理No / 機番 / 機種（部分一致検索）
  - 担当者（複数選択可）
  - 進捗ステータス（複数選択可）
  - 作業区分（複数選択可）
  - 日付範囲（仕掛日、完了日、作図期限）
- **ソート**: 各列でソート可能
- **表示項目**: 管理No, 機種, 機番, 担当者, 進捗, 予定工数, 実績工数, 作図期限

#### 1.3 案件詳細
- **基本情報タブ**: 全項目表示・編集
- **工数タブ**: 案件の工数履歴一覧（日付、時間、担当者、内容）
- **資料タブ**:
  - 機種の資料一覧（自動紐づけ）
  - 機番の資料一覧（自動紐づけ）
  - 誰でも追加可能（URL or ファイルアップロード）
  - 検索・プレビュー対応
- **注意点タブ**:
  - 機種カテゴリに基づく注意点チェックリスト
  - 必須/推奨の表示
  - 完了チェック機能
  - 自由追記 → テンプレ昇格機能

#### 1.4 進捗変更時のトリガー
- **仕掛日トリガー**: 進捗マスタで設定されたステータスに変更時、仕掛日を自動入力
- **完了日トリガー**: 完了ステータスに変更時、完了日を自動入力
- **進捗記入者**: 進捗変更時に自動記録
- **更新日時**: 編集時に自動更新

---

### 2. 工数管理

#### 2.1 工数入力（月グリッドUI）

**スプレッドシート操作感の再現**:

```
┌─────────────────────────────────────────────────────┐
│ 工数入力: 2025年9月                    [←8月 10月→] │
├─────────────────────────────────────────────────────┤
│                                                     │
│ 管理No  | 機番  | 1  2  3  4  5 ... 30 31 | 合計   │
│─────────┼───────┼──────────────────┼───────│
│ E25A001 | HMX7  |    1.5 2.0 1.0  ...     | 15.5h │
│ E25A002 | STX10 | 0.5    1.5      ...     | 8.0h  │
│ E25A003 | NEX30 |       [+]       ...     | 0.0h  │
│                                                     │
│ 日別合計:        0.5 1.5 3.5 1.0  ...              │
└─────────────────────────────────────────────────────┘
```

**操作仕様**:
- セルクリックで直接編集（0.25刻み）
- `1:30` や `90m` 入力 → 自動で `1.5` に変換
- `=+0.25` で加算、`=-0.25` で減算
- 矢印キーで移動、Enter で確定、Tab で右移動
- Excel/スプレッドシートからコピー貼り付け対応
- ドラッグで複数セル選択 → 一括入力
- 土日祝日は淡色表示
- 未来日は入力警告

**スマホ対応**:
- セルタップ → テンキーダイアログ
- `+15m` / `-15m` ボタン
- 横スクロールで日付移動
- 行固定ヘッダ（案件名・月合計は常時表示）

#### 2.2 工数集計
- 案件別実績工数の自動集計（案件詳細に表示）
- 担当者別月次集計（ダッシュボード）
- 作業区分別集計（レポート）
- 予定工数 vs 実績工数の差異分析

#### 2.3 データ保存
- **内部保存**: 分単位（整数）で保存
- **表示**: 小数時間（0.25刻み）で表示
- **API**: 差分パッチ方式で更新（変更セルのみ送信）

---

### 3. 請求管理

#### 3.1 請求書生成フロー
1. **請求月選択**: プルダウンで年月選択（YYYY-MM形式）
2. **対象抽出**: 選択月に完了日がある案件を自動抽出
3. **プレビュー**: 請求明細をテーブル表示
   - 管理No / 業務委託内容 / 実工数（時間、小数）
4. **Excel出力**: 3列固定のExcelファイル生成（テンプレ適用）
5. **請求確定**:
   - 確定ボタン押下で締め処理
   - 当月の工数セルを読み取り専用化
   - 確定ログ記録（誰が・いつ）

#### 3.2 請求書Excel仕様
- **列構成** (固定):
  1. 管理No
  2. 業務委託内容（機番）
  3. 実工数（時間）
- **実工数計算**:
  - 当月の全担当者の工数合計
  - 分単位で集計 → 最後に小数時間変換（合計分 ÷ 60）
  - 0.25刻みで正確に出力
- **サンプル**:
```
管理No    | 業務委託内容 | 実工数(時間)
E25A001  | HMX7-CN2    | 5.75
E25A002  | STX10S2VS1  | 3.25
```

#### 3.3 請求確定権限
- 全員が請求書プレビュー可能
- 確定操作のみ管理者ロール限定（オプション）
- 確定後の工数修正は管理者のみ可能

---

### 4. 資料管理

#### 4.1 資料集ハブ
- **正規URL**:
  - `/collections/model/{機種}` - 機種別資料集
  - `/collections/machine/{機番}` - 機番別資料集
- **短縮URL**: `/go/m/{機種}`, `/go/n/{機番}` でリダイレクト
- **案件との連携**:
  - 「機番(リンク)」列 → 機番の資料集URL
  - 「STD資料(リンク)」列 → 機種の資料集URL

#### 4.2 資料追加
- 誰でも追加可能
- URL登録 or ファイルアップロード（S3互換ストレージ）
- タイトル、説明、タグ設定
- PDF/画像はインラインプレビュー

#### 4.3 資料検索
- タイトル・タグ・拡張子で検索
- 一覧（カード/テーブル切替）
- 並び替え（登録日、タイトル順）

---

### 5. 資料作成注意点チェックリスト

#### 5.1 テンプレート展開
- **タイミング**: 案件作成時（PDF取込時）
- **カテゴリ判定**: 機種から自動判定（H0, NEX, B板など）
- **展開内容**: 該当カテゴリの注意点を案件にコピー

#### 5.2 チェック項目管理
- **表示**: 案件詳細の「注意点」タブ
- **項目追加**:
  - テンプレから選択
  - 自由入力（案件ローカル）
  - 「テンプレに昇格」チェックでマスタ登録
- **完了処理**:
  - チェックボックスで完了
  - 完了者・完了日時を自動記録
- **警告**:
  - 請求確定時に必須項目が未完なら警告（ブロックはしない）

#### 5.3 テンプレート管理
- マスタ管理画面から編集可能
- カテゴリ・タイトル・詳細・重要度・並び順
- 自動補足コメント（選択時に自動入力）

---

### 6. ダッシュボード

#### 6.1 サマリー情報
- **個人**: 今月の自分の工数合計
- **全体**: 全体工数、案件数、進捗分布（円グラフ）
- **期限**: 今週締切の案件リスト
- **注意点**: 未完の必須チェック項目数

#### 6.2 最近の活動
- 自分の担当案件（最近更新順）
- 直近のPDF取込状況

---

### 7. マスタ管理

#### 7.1 管理画面
- **対象マスタ**:
  - 進捗マスタ
  - 作業区分マスタ
  - 問い合わせマスタ
  - 注意点テンプレート
- **操作**:
  - 一覧表示（並び順ドラッグ変更）
  - 追加・編集・無効化
  - 色設定（進捗・作業区分）
  - トリガー設定（進捗マスタ）

#### 7.2 参照整合性
- 無効化されたマスタ値は新規選択不可
- 既存データは表示のみ（削除はしない）

---

## 🎨 画面設計

### 画面一覧

| No | 画面名 | URL | 実装状況 |
|----|--------|-----|---------|
| 1 | ログイン | `/login` | ✅ 完了 |
| 2 | ユーザー登録 | `/register` | ✅ 完了 |
| 3 | ダッシュボード | `/dashboard` | ⚠️ 要強化 |
| 4 | 案件一覧 | `/projects` | ⚠️ 要強化 |
| 5 | 案件詳細 | `/projects/{id}` | ❌ 未実装 |
| 6 | 案件登録 | `/projects/new` | ❌ 未実装 |
| 7 | 工数入力（グリッド） | `/worklogs/grid` | ❌ 未実装 |
| 8 | 請求管理 | `/invoices` | ❌ 未実装 |
| 9 | 請求書詳細 | `/invoices/{id}` | ❌ 未実装 |
| 10 | マスタ管理 | `/masters` | ❌ 未実装 |
| 11 | PDFインポート | `/import` | ❌ 未実装 |
| 12 | 資料集 | `/collections/{type}/{key}` | ❌ 未実装 |

---

## 🔌 API設計

### 主要エンドポイント

#### 案件管理
```
POST   /api/import/pdf              PDF解析・インポート
GET    /api/import/jobs/:id         インポートジョブ状態取得
POST   /api/projects                案件確定登録
GET    /api/projects                案件一覧（検索・フィルタ）
GET    /api/projects/:id            案件詳細
PUT    /api/projects/:id            案件更新
GET    /api/projects/my             自分の担当案件
```

#### 工数管理
```
GET    /api/worklogs/grid?month=YYYY-MM  月グリッドデータ取得
PUT    /api/worklogs/grid                差分パッチ更新
POST   /api/worklogs                     工数個別登録
GET    /api/worklogs/summary             集計データ取得
```

#### 請求管理
```
GET    /api/invoices?month=YYYY-MM       請求プレビュー
POST   /api/invoices/close               請求締め確定
GET    /api/invoices/export?month=YYYY-MM Excel出力
```

#### 資料管理
```
GET    /api/materials?scope={model|machine}&key={value}  資料一覧
POST   /api/materials                                    資料追加
PUT    /api/materials/:id                                資料更新
DELETE /api/materials/:id                                資料削除
```

#### 注意点管理
```
GET    /api/checklist/templates?category={category}  テンプレ取得
POST   /api/checklist/templates                      テンプレ追加
GET    /api/projects/:id/checklist                   案件のチェック項目
POST   /api/projects/:id/checklist                   項目追加
PUT    /api/projects/:id/checklist/:itemId           項目更新（完了など）
```

#### マスタ管理
```
GET    /api/masters/shinchoku        進捗マスタ一覧
POST   /api/masters/shinchoku        進捗マスタ追加
PUT    /api/masters/shinchoku/:id    進捗マスタ更新
GET    /api/masters/sagyou-kubun     作業区分マスタ一覧
GET    /api/masters/toiawase         問い合わせマスタ一覧
```

---

## 🚀 実装優先順位

### Phase 1: MVP基盤（2-3週間）

**目標**: 既存スプレッドシートの基本機能をWeb化

1. **マスタ管理機能**
   - 進捗・作業区分・問い合わせマスタのCRUD
   - マスタ管理画面

2. **案件管理強化**
   - 全項目対応
   - 案件詳細画面（基本情報タブ）
   - 検索・フィルタ強化

3. **工数グリッドUI**
   - 月グリッド表示
   - セル編集（15分刻み）
   - Excel貼り付け対応

### Phase 2: 自動化・資料管理（2-3週間）

4. **PDF自動取り込み**
   - OCR処理（Tesseract）
   - 確認テーブルUI
   - バッチインポート

5. **資料集ハブ**
   - 機種・機番別資料一覧
   - 資料追加・検索
   - 案件との連携

6. **注意点チェックリスト**
   - テンプレート管理
   - 案件へのチェック項目展開
   - 完了管理

### Phase 3: 請求・集計（1-2週間）

7. **請求管理機能**
   - 請求月選択
   - Excel出力（3列固定）
   - 請求締め処理

8. **工数集計・ダッシュボード強化**
   - 担当者別・月別集計
   - サマリー表示
   - 期限アラート

### Phase 4: 最適化・運用（1週間）

9. **モバイル対応最適化**
10. **監査ログ・バックアップ**
11. **パフォーマンス最適化**

---

## 📝 非機能要件

### パフォーマンス
- API応答時間: 500ms以内
- 同時接続ユーザー数: 50人
- 工数グリッド: 1000行×31列まで快適動作

### セキュリティ
- JWT認証（有効期限: 24時間）
- パスワードハッシュ化（bcrypt）
- XSS・CSRF対策
- SQLインジェクション対策（ORM使用）

### 可用性
- 稼働率: 99%以上（目標）
- バックアップ:
  - DB日次スナップショット90日保持
  - 監査ログ1年保持
  - 生成Excel90日保持

### ユーザビリティ
- レスポンシブデザイン
- モバイル対応（スマホ・タブレット）
- 操作マニュアル整備

### データ整合性
- 工数の実績自動集計（手動編集不可）
- 進捗記入者・更新日時の自動記録
- 請求締め後の工数ロック

---

## 🔄 移行計画

### 移行ステップ
1. **並行運用期間（1ヶ月）**
   - Phase 1完了後、既存GASと新システムを並行運用
   - データ整合性チェック

2. **段階的移行**
   - Phase 2完了後: マスタデータ・案件データ移行
   - Phase 3完了後: 請求データ移行

3. **完全移行**
   - 全機能テスト完了後
   - ユーザートレーニング実施
   - GASシステムのバックアップ保管

### 初期データ移行
- `テストシート.xlsx` → 案件・工数データ
- `資料作成注意点一覧.xlsx` → チェックリストテンプレート
- 既存マスタ → 進捗・作業区分・問い合わせマスタ

---

## 📚 参考資料

- [既存GASリポジトリ](https://github.com/ACSshiga/my-gas-spreadsheet-script-nissei)
- アップロード済みファイル:
  - `docs/2025-9-22.pdf` - 委託書サンプル（39ページ）
  - `docs/テストシート.xlsx` - 既存工数管理シート
  - `docs/請求書.xlsx` - 請求書フォーマット
  - `docs/資料作成注意点一覧.xlsx` - 機種別注意事項

---

## ✅ 確定済み要件（ユーザー回答反映）

### 1. 機種の分類ルール
**決定事項**: 自動分類アルゴリズムで対応し、成果物を見て調整する方針
**実装方針**:
- 正規表現による自動分類（シリーズ、世代、トン数、仕様コードを抽出）
- 機種マスタテーブルで手動登録・編集可能
- 未分類の場合はデフォルトで「その他」カテゴリ
- 分類結果を機種編集画面で確認・調整可能

**自動分類ルール（初期実装）**:
```python
# 例: FNX140Ⅳ-36AK → series="FNX", tonnage=140, generation="Ⅳ", spec="36AK"
pattern = r"([A-Z]+)(\d+)?([ⅠⅡⅢⅣⅤⅥⅦⅧⅨⅩiivxIIVX]*)-?(.+)?"
```

### 2. 注意点チェックリストの担当者
**決定事項**: 実装後に成果物を見て決定（まずは全員が完了可能な運用で開始）
**Phase 1実装**:
- assignee_user_id は nullable で実装
- 完了者（completed_by）は必須記録
- Phase 2で担当者割当機能を追加するか判断

### 3. 請求確定後の工数修正ポリシー
**決定事項**: 工数修正 → 実績合計に自動反映（請求書は再生成不要）
**実装仕様**:
- 請求確定後も工数入力は可能（制限なし）
- 工数変更時、案件の実績工数を自動再集計
- 請求書の実績工数は確定時点のスナップショット（手動で再生成しない限り更新されない）
- 管理者が「請求書を再生成」ボタンで最新工数に更新可能

### 4. 工数グリッドの作業区分
**決定事項**: 1セルに複数の作業区分を含める
**実装仕様**:
- 1セル = 1案件 × 1日の合計時間
- 作業区分は work_logs テーブルで個別管理
- グリッド表示は日別合計のみ
- セルをクリック → 詳細ダイアログで作業区分ごとの内訳を表示・編集

### 5. ファイルストレージ
**決定事項**: Google Drive / S3 は不要（資料管理は URL ベース）
**実装仕様**:
- アップロード機能は実装しない（Phase 1では URL 登録のみ）
- materials テーブルの kind は 'link' のみ対応
- 将来的にローカルストレージ対応を検討可能

### 6. PDFのOCR精度
**決定事項**: 文字が読める範囲でベストエフォート
**実装仕様**:
- Tesseract OCR で抽出
- 精度目標: 70%以上（手動確認前提）
- 抽出失敗時は空欄表示 + 手動入力
- フォーマット統一前提（手書き対応は Phase 2以降）

### 7. 資料のファイルサイズ制限
**決定事項**: 大きすぎなければ OK（常識的な範囲）
**実装仕様**:
- Phase 1: ファイルアップロードは実装しない（URL のみ）
- Phase 2でアップロード対応時: 上限 50MB、形式は PDF/画像/Office 文書

### 8. モバイル対応の範囲
**決定事項**: 全機能をモバイル対応
**実装仕様**:
- レスポンシブデザイン（画面サイズに応じて自動調整）
- 工数グリッド: スマホ専用 UI（タップ + テンキー）
- 案件登録・請求確定もスマホで可能

### 9. 通知機能
**決定事項**: Phase 1では実装しない（将来対応の可能性あり）

### 10. エクスポート機能
**決定事項**: Phase 1では実装しない（請求書 Excel 出力のみ）
**将来対応の可能性**: CSV/PDF/JSON API

---

## ✅ 次のステップ

1. ✅ **要件確定完了** - 全ての残課題に対する回答を反映
2. **Phase 1 実装開始**:
   - マスタ管理機能（進捗・作業区分・問い合わせ）
   - 案件管理強化（全項目対応 + 詳細画面）
   - 工数グリッドUI（月グリッド + セル編集 + Excel貼り付け）
3. **機種分類アルゴリズムの実装とテスト**
4. **モバイルUIのレスポンシブ対応**

---

**ドキュメント管理**:
- ファイル名: `nissei-requirements-definition-v1.0.md`
- 更新履歴:
  - v1.0 (2025-09-30) - 初版作成
  - v1.1 (2025-09-30) - ユーザー回答反映、全要件確定