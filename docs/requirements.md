# Nissei 工数管理システム 要件定義書

## 📋 プロジェクト概要

### 目的
既存のGoogle Spreadsheet + Apps Scriptベースの工数管理システムを、FastAPI + Next.jsによるWebアプリケーションに完全移行し、以下を実現する：

1. **業務の効率化**: データ同期の完全自動化により、二重入力や転記作業を撲滅
2. **正確性の向上**: 手作業を排除し、ヒューマンエラーのない正確なデータ管理
3. **情報共有の円滑化**: 各担当者が必要な情報に、他のメンバーを気にせずアクセス可能
4. **スケーラビリティ**: スプレッドシートの制約（同時編集、パフォーマンス）からの解放

### 対象業務
- 設計業務の進捗管理
- 工数入力・集計
- 委託書PDFからの自動データ取り込み
- 請求書データ生成
- 資料フォルダ管理（Google Drive連携）

---

## 🗂️ 既存システム分析

### 現状のシート構成

| シート種別 | シート名 | 役割 |
|-----------|---------|------|
| **マスターデータ** | メインシート | 全案件のマスターデータ（情報の原本） |
| **作業用シート** | 工数_{担当者名} | 担当者ごとの作業用シート（日々の工数入力） |
| **出力用シート** | 請求シート | 指定月の請求データ自動出力 |
|  | ソートビュー | メインシートのソート・フィルタリング用 |
| **設定用シート** | 担当者マスタ | 担当者名・メール・色分け |
|  | 進捗マスタ | 進捗ステータス・色分け・トリガー設定 |
|  | 作業区分マスタ | 作業区分の選択肢と色分け |
|  | 問い合わせマスタ | 問い合わせステータス・色分け |

### メインシートのデータ項目

```
管理No, 作業区分, 機番, 機種, 機番(リンク), STD資料(リンク), 参考製番,
回路図番, 問い合わせ, 仮コード, 担当者, 納入先, 予定工数, 実績工数,
進捗, 仕掛日, 完了日, 作図期限, 進捗記入者, 更新日時, 係り超過理由,
注意点, 備考
```

### 工数シートのデータ項目

```
管理No, 作業区分, 機番, 進捗, 予定工数, 実績工数合計, [日付列（動的）]
```

---

## 🎯 機能要件

### 1. 認証・ユーザー管理

#### 1.1 ユーザー認証
- ✅ **実装済み**: JWT認証（Email + Password）
- ✅ **実装済み**: ユーザー登録
- ✅ **実装済み**: ログイン・ログアウト
- ❌ **未実装**: パスワードリセット機能
- ❌ **未実装**: セッション管理（トークンリフレッシュ）

#### 1.2 ユーザー属性
```python
User:
  - id (UUID)
  - email (unique)
  - username
  - role (admin/worker) # 追加必要
  - color (担当者色分け用) # 追加必要
  - created_at
  - updated_at
```

---

### 2. マスタ管理機能

#### 2.1 担当者マスタ
- **目的**: 工数入力者の管理、シート自動生成、色分け
- **項目**:
  - 担当者名（ユーザーテーブルと連携）
  - メールアドレス
  - 背景色（担当者セル色付け用）
  - 有効/無効フラグ

#### 2.2 進捗マスタ
- **目的**: 進捗ステータスの管理とトリガー設定
- **項目**:
  - 進捗ステータス名（例: 未着手、進行中、完了、保留）
  - 背景色
  - 完了日トリガー（TRUE時に完了日自動入力）
  - 仕掛日トリガー（TRUE時に仕掛日自動入力）
  - 並び順

#### 2.3 作業区分マスタ
- **目的**: 作業の分類管理
- **項目**:
  - 作業区分名（例: 盤配、線加工、委託）
  - 背景色
  - 並び順

#### 2.4 問い合わせマスタ
- **目的**: 問い合わせステータス管理
- **項目**:
  - 問い合わせステータス名
  - 背景色
  - 並び順

#### 2.5 機種マスタ（新規）
- **目的**: 資料作成注意点一覧の管理
- **項目**:
  - 機種シリーズ（TC15系、NEX30系など）
  - 注意事項カテゴリ
  - 注意事項詳細
  - 参照URL・画像

---

### 3. 案件管理機能

#### 3.1 案件登録
- ✅ **実装済み**: 基本的な案件作成API
- ❌ **未実装**: 以下の項目対応
  - 機番(リンク) - Google Drive URL
  - STD資料(リンク) - Google Drive URL
  - 参考製番
  - 回路図番
  - 問い合わせステータス
  - 仮コード
  - 作図期限
  - 進捗記入者
  - 係り超過理由
  - 注意点
  - 備考

#### 3.2 案件編集
- ✅ **実装済み**: 基本的な案件更新API
- ❌ **未実装**:
  - 担当者変更時の自動通知
  - 進捗変更時のトリガー処理
    - 仕掛日の自動入力
    - 完了日の自動入力
    - 顧客用管理表への同期

#### 3.3 案件一覧・検索
- ✅ **実装済み**: 基本的な一覧表示
- ✅ **実装済み**: ステータスフィルタ
- ✅ **実装済み**: 管理No/機番検索
- ❌ **未実装**:
  - 担当者フィルタ
  - 作業区分フィルタ
  - 日付範囲フィルタ（仕掛日、完了日、作図期限）
  - ソート機能強化
  - ページネーション改善

#### 3.4 担当者専用ビュー
- **GAS機能**: 「自分の担当案件のみ表示」
- **要件**: ログインユーザーに割り当てられた案件のみ表示
- ❌ **未実装**

---

### 4. 工数入力・管理機能

#### 4.1 日次工数入力
- ✅ **実装済み**: 基本的な工数入力
- ✅ **実装済み**: 案件選択
- ✅ **実装済み**: 作業日・開始時刻・終了時刻
- ✅ **実装済み**: 作業時間（分）
- ✅ **実装済み**: 作業内容（メモ）
- ❌ **未実装**:
  - カレンダーUIでの日別工数入力
  - 土日祝日の色分け表示
  - 月ごとの工数入力シート切り替え

#### 4.2 工数集計
- ❌ **未実装**:
  - 案件別実績工数の自動集計
  - 担当者別工数集計
  - 月別工数集計
  - 作業区分別工数集計
  - 予定工数 vs 実績工数の差異分析

#### 4.3 工数同期
- **GAS機能**: 工数シート → メインシートへの自動同期
- **要件**:
  - 工数入力時に案件の実績工数を自動更新
  - 進捗変更時にメインシートへ反映
  - 更新日時・進捗記入者の自動記録
- ❌ **未実装**

---

### 5. PDF自動取り込み機能

#### 5.1 委託書PDFのインポート
- **GAS機能**:
  - 指定フォルダのPDFを自動解析
  - OCRによるテキスト抽出
  - メインシートへ自動登録
  - 処理済みPDFの移動

- **抽出項目**:
  - 管理No（E25A001形式）
  - 機種
  - 機番
  - 納入先
  - 作業区分（盤配/線加工を自動判定）
  - 予定工数
  - 作図期限

- ❌ **未実装**

#### 5.2 バッチ処理
- **GAS機能**: 複数PDFの一括処理
- **要件**:
  - フォルダ内の全PDFを順次処理
  - エラーハンドリング（解析失敗時のログ出力）
  - 処理結果のサマリー表示
- ❌ **未実装**

---

### 6. 請求管理機能

#### 6.1 請求書データ生成
- **GAS機能**:
  - 指定月の完了案件を自動抽出
  - 請求シートへ出力
  - 管理No、委託業務内容、作業区分、予定工数、実工数

- ❌ **未実装**:
  - 請求月選択UI
  - 完了日によるフィルタリング
  - 請求書PDF生成
  - 単価計算（¥4,500/時間）
  - 請求額合計

#### 6.2 請求書出力
- ❌ **未実装**:
  - PDF出力
  - Excel出力
  - 請求書テンプレート管理
  - 委託先情報（長野エージェンエス）

---

### 7. Google Drive連携

#### 7.1 資料フォルダ自動生成
- **GAS機能**:
  - 機番フォルダの自動作成
  - STD資料フォルダの自動作成
  - フォルダURLのメインシートへの自動挿入
  - 顧客用管理表の自動生成（テンプレートからコピー）

- **フォルダ構成**:
  ```
  REFERENCE_MATERIAL_PARENT/
    ├── {機番}/
    │   └── {機番}盤配指示図出図管理表

  SERIES_MODEL_PARENT/
    └── {機種}/
  ```

- ❌ **未実装**

#### 7.2 顧客用管理表の自動更新
- **GAS機能**:
  - 仕掛日入力時: 機種・製番を管理表に記入
  - 完了日入力時: 完了日を管理表に記入
  - リトライ機能（接続エラー時）

- ❌ **未実装**

---

### 8. バックアップ機能

#### 8.1 週次バックアップ
- **GAS機能**:
  - スプレッドシート全体のコピー
  - バックアップフォルダへ保存
  - タイムスタンプ付きファイル名
  - 古いバックアップの自動削除（5世代保持）

- ❌ **未実装**

#### 8.2 データエクスポート
- ❌ **未実装**:
  - CSV出力
  - Excel出力
  - JSON出力

---

### 9. 色分け・書式設定

#### 9.1 セル色分けルール
- **GAS機能**:
  - 進捗ステータスによる行の色分け
  - 担当者による色分け
  - 作業区分による色分け
  - 問い合わせステータスによる色分け
  - 交互行の背景色

- ❌ **未実装**

#### 9.2 カレンダー色分け
- **GAS機能**:
  - 土日の背景色
  - 祝日の背景色（日本の祝日カレンダー連携）

- ❌ **未実装**

---

### 10. 通知機能（新規）

#### 10.1 担当者通知
- ❌ **未実装**:
  - 案件アサイン時の通知
  - 作図期限前のリマインダー
  - 進捗変更の通知

#### 10.2 管理者通知
- ❌ **未実装**:
  - 係り超過案件の通知
  - 期限遅延案件の通知

---

## 📊 データモデル設計

### ER図（概要）

```
User (ユーザー)
  ├─→ Project (案件) [担当者]
  ├─→ WorkLog (工数入力)
  └─→ MasterTantousha (担当者マスタ)

Project (案件)
  ├─→ WorkLog (工数入力) [多]
  ├─→ Material (資料) [多]
  ├─→ Checklist (チェックリスト) [多]
  ├─→ MasterSagyouKubun (作業区分マスタ)
  ├─→ MasterShinchoku (進捗マスタ)
  └─→ MasterToiawase (問い合わせマスタ)

Invoice (請求書)
  └─→ Project (案件) [多] （完了日による抽出）
```

### データベーステーブル定義

#### 既存テーブル

##### users（ユーザー）
```sql
- id: UUID PRIMARY KEY
- email: VARCHAR UNIQUE NOT NULL
- username: VARCHAR NOT NULL
- hashed_password: VARCHAR NOT NULL
- role: VARCHAR DEFAULT 'worker' -- 追加
- color: VARCHAR -- 追加（担当者色）
- is_active: BOOLEAN DEFAULT true
- created_at: TIMESTAMP
- updated_at: TIMESTAMP
```

##### projects（案件）
```sql
✅ 既存:
- id: UUID PRIMARY KEY
- user_id: UUID FOREIGN KEY
- management_no: VARCHAR UNIQUE NOT NULL (管理No)
- machine_no: VARCHAR (機番)
- series: VARCHAR (機種)
- status: VARCHAR (進捗)
- estimated_hours: INTEGER (予定工数・分)
- actual_hours: INTEGER (実績工数・分)
- start_date: DATE (仕掛日)
- created_at: TIMESTAMP
- updated_at: TIMESTAMP

❌ 追加必要:
- sagyou_kubun_id: UUID FOREIGN KEY (作業区分)
- machine_url: VARCHAR (機番リンク)
- std_material_url: VARCHAR (STD資料リンク)
- reference_kiban: VARCHAR (参考製番)
- circuit_diagram_no: VARCHAR (回路図番)
- toiawase_status_id: UUID (問い合わせ)
- temp_code: VARCHAR (仮コード)
- destination: VARCHAR (納入先)
- complete_date: DATE (完了日)
- drawing_deadline: DATE (作図期限)
- progress_editor: VARCHAR (進捗記入者)
- overrun_reason: TEXT (係り超過理由)
- notes: TEXT (注意点)
- remarks: TEXT (備考)
```

##### work_logs（工数入力）
```sql
✅ 既存:
- id: UUID PRIMARY KEY
- user_id: UUID FOREIGN KEY
- project_id: UUID FOREIGN KEY
- work_date: DATE NOT NULL
- start_time: TIME
- end_time: TIME
- duration_minutes: INTEGER NOT NULL
- work_content: TEXT
- created_at: TIMESTAMP
- updated_at: TIMESTAMP
```

#### 追加必要なテーブル

##### master_tantousha（担当者マスタ）
```sql
- id: UUID PRIMARY KEY
- user_id: UUID FOREIGN KEY (usersテーブルと連携)
- name: VARCHAR NOT NULL
- email: VARCHAR UNIQUE NOT NULL
- background_color: VARCHAR
- is_active: BOOLEAN DEFAULT true
- created_at: TIMESTAMP
- updated_at: TIMESTAMP
```

##### master_shinchoku（進捗マスタ）
```sql
- id: UUID PRIMARY KEY
- status_name: VARCHAR UNIQUE NOT NULL
- background_color: VARCHAR
- completion_trigger: BOOLEAN DEFAULT false (完了日トリガー)
- start_date_trigger: BOOLEAN DEFAULT false (仕掛日トリガー)
- sort_order: INTEGER
- created_at: TIMESTAMP
- updated_at: TIMESTAMP
```

##### master_sagyou_kubun（作業区分マスタ）
```sql
- id: UUID PRIMARY KEY
- kubun_name: VARCHAR UNIQUE NOT NULL
- background_color: VARCHAR
- sort_order: INTEGER
- created_at: TIMESTAMP
- updated_at: TIMESTAMP
```

##### master_toiawase（問い合わせマスタ）
```sql
- id: UUID PRIMARY KEY
- status_name: VARCHAR UNIQUE NOT NULL
- background_color: VARCHAR
- sort_order: INTEGER
- created_at: TIMESTAMP
- updated_at: TIMESTAMP
```

##### master_kishu_notes（機種別注意事項）
```sql
- id: UUID PRIMARY KEY
- series: VARCHAR NOT NULL (機種シリーズ)
- category: VARCHAR (カテゴリ)
- note_content: TEXT NOT NULL
- reference_url: VARCHAR
- image_url: VARCHAR
- created_at: TIMESTAMP
- updated_at: TIMESTAMP
```

##### invoices（請求書）
```sql
- id: UUID PRIMARY KEY
- invoice_month: DATE NOT NULL (請求月)
- total_hours: INTEGER (合計工数)
- total_amount: DECIMAL (合計金額)
- hourly_rate: DECIMAL DEFAULT 4500 (時間単価)
- status: VARCHAR DEFAULT 'draft' (draft/sent/paid)
- created_at: TIMESTAMP
- updated_at: TIMESTAMP
```

##### invoice_items（請求書明細）
```sql
- id: UUID PRIMARY KEY
- invoice_id: UUID FOREIGN KEY
- project_id: UUID FOREIGN KEY
- management_no: VARCHAR
- work_content: VARCHAR
- sagyou_kubun: VARCHAR
- estimated_hours: INTEGER
- actual_hours: INTEGER
- amount: DECIMAL
- created_at: TIMESTAMP
```

##### pdf_import_logs（PDFインポートログ）
```sql
- id: UUID PRIMARY KEY
- file_name: VARCHAR NOT NULL
- file_size: INTEGER
- import_status: VARCHAR (success/failed)
- imported_count: INTEGER
- error_message: TEXT
- processed_at: TIMESTAMP
```

##### drive_folders（Driveフォルダ管理）
```sql
- id: UUID PRIMARY KEY
- project_id: UUID FOREIGN KEY
- folder_type: VARCHAR (kiban/std_material/management_sheet)
- folder_url: VARCHAR NOT NULL
- folder_id: VARCHAR NOT NULL (Drive Folder ID)
- created_at: TIMESTAMP
```

---

## 🎨 画面設計

### 画面一覧

| No | 画面名 | URL | 実装状況 |
|----|--------|-----|---------|
| 1 | ログイン | `/login` | ✅ 完了 |
| 2 | ユーザー登録 | `/register` | ✅ 完了 |
| 3 | ダッシュボード | `/dashboard` | ✅ 完了（要強化） |
| 4 | 案件一覧 | `/projects` | ✅ 完了（要強化） |
| 5 | 案件詳細 | `/projects/{id}` | ❌ 未実装 |
| 6 | 案件登録 | `/projects/new` | ❌ 未実装 |
| 7 | 工数入力 | `/worklogs` | ✅ 完了（要強化） |
| 8 | 工数カレンダー | `/worklogs/calendar` | ❌ 未実装 |
| 9 | 請求管理 | `/invoices` | ❌ 未実装 |
| 10 | 請求書詳細 | `/invoices/{id}` | ❌ 未実装 |
| 11 | マスタ管理 | `/masters` | ❌ 未実装 |
| 12 | PDFインポート | `/import` | ❌ 未実装 |
| 13 | 設定 | `/settings` | ❌ 未実装 |

### 主要画面のワイヤーフレーム要件

#### 3. ダッシュボード（強化）
```
┌─────────────────────────────────────────┐
│ Nissei 工数管理システム    [ユーザー名▼] │
├─────────────────────────────────────────┤
│ 📊 サマリー                              │
│ ┌──────┬──────┬──────┬──────┐          │
│ │進行中 │完了   │保留   │今月工数│          │
│ │  12  │  45  │   3  │ 320h │          │
│ └──────┴──────┴──────┴──────┘          │
│                                         │
│ 📌 自分の担当案件 (最近更新)             │
│ ┌─────────────────────────────────┐    │
│ │ E25A001 | NEX30 | 進行中 | 2h/5h  │    │
│ │ E25A002 | TC15  | 完了   | 3h/3h  │    │
│ └─────────────────────────────────┘    │
│                                         │
│ ⚠️  期限間近の案件                       │
│ ┌─────────────────────────────────┐    │
│ │ E25A003 | 作図期限: あと2日       │    │
│ └─────────────────────────────────┘    │
└─────────────────────────────────────────┘
```

#### 5. 案件詳細（新規）
```
┌─────────────────────────────────────────┐
│ 案件詳細: E25A001                [編集] │
├─────────────────────────────────────────┤
│ 基本情報                                │
│ 管理No: E25A001                         │
│ 作業区分: 盤配                          │
│ 機番: HMX7-CN2                          │
│ 機種: NEX30                             │
│ 納入先: ○○株式会社                      │
│                                         │
│ 進捗情報                                │
│ 担当者: 山田太郎                        │
│ ステータス: 進行中                      │
│ 仕掛日: 2025/09/01                      │
│ 作図期限: 2025/09/30                    │
│                                         │
│ 工数情報                                │
│ 予定工数: 5時間                         │
│ 実績工数: 2時間30分                     │
│ 進捗率: 50%                             │
│                                         │
│ 📂 関連資料                             │
│ [機番フォルダ] [STD資料] [管理表]       │
│                                         │
│ 📝 工数履歴                             │
│ ┌─────────────────────────────────┐    │
│ │ 2025/09/28 | 1.5h | 配線図作成  │    │
│ │ 2025/09/27 | 1.0h | 図面確認    │    │
│ └─────────────────────────────────┘    │
└─────────────────────────────────────────┘
```

#### 8. 工数カレンダー（新規）
```
┌─────────────────────────────────────────┐
│ 工数入力（カレンダー）        2025年9月  │
├─────────────────────────────────────────┤
│ 案件: [E25A001 - NEX30 ▼]              │
│                                         │
│ 日 月 火 水 木 金 土                     │
│ 1  2  3  4  5  6  7                     │
│             2h 3h 2h                    │
│ 8  9  10 11 12 13 14                    │
│ 1h 2h 2h 1h 3h 2h                       │
│ 15 16 17 18 19 20 21                    │
│         1h 2h 2h                        │
│ 22 23 24 25 26 27 28                    │
│ 2h 2h 1h 2h [+] 1h                      │
│ 29 30                                   │
│ 1h [+]                                  │
│                                         │
│ 今月の合計: 32時間                      │
└─────────────────────────────────────────┘
```

#### 9. 請求管理（新規）
```
┌─────────────────────────────────────────┐
│ 請求管理                    [新規作成]  │
├─────────────────────────────────────────┤
│ 請求月: [2025年9月 ▼]                   │
│                                         │
│ 請求先: 長野エージェンエス              │
│ 単価: ¥4,500/時間                       │
│                                         │
│ 請求明細                                │
│ ┌─────────────────────────────────┐    │
│ │管理No│業務内容│工数│金額      │    │
│ │E25A001│盤配   │5h │¥22,500  │    │
│ │E25A002│線加工 │3h │¥13,500  │    │
│ │E25A003│盤配   │8h │¥36,000  │    │
│ └─────────────────────────────────┘    │
│                                         │
│ 合計工数: 16時間                        │
│ 合計金額: ¥72,000                       │
│                                         │
│ [PDF出力] [Excel出力]                   │
└─────────────────────────────────────────┘
```

---

## 🔌 API設計

### API仕様概要

#### 認証系API
```
✅ POST   /api/auth/register      ユーザー登録
✅ POST   /api/auth/login         ログイン
❌ POST   /api/auth/logout        ログアウト
❌ POST   /api/auth/refresh       トークンリフレッシュ
❌ POST   /api/auth/reset-password パスワードリセット
```

#### 案件管理API
```
✅ GET    /api/projects           案件一覧取得
✅ POST   /api/projects           案件作成
✅ GET    /api/projects/{id}      案件詳細取得
✅ PUT    /api/projects/{id}      案件更新
❌ DELETE /api/projects/{id}      案件削除
❌ GET    /api/projects/my        自分の担当案件
❌ GET    /api/projects/summary   サマリー情報
```

#### 工数管理API
```
✅ GET    /api/worklogs           工数一覧取得
✅ POST   /api/worklogs           工数登録
✅ DELETE /api/worklogs/{id}      工数削除
❌ GET    /api/worklogs/calendar  カレンダー形式取得
❌ GET    /api/worklogs/summary   工数集計
```

#### マスタ管理API
```
❌ GET    /api/masters/tantousha       担当者マスタ一覧
❌ POST   /api/masters/tantousha       担当者マスタ作成
❌ GET    /api/masters/shinchoku       進捗マスタ一覧
❌ POST   /api/masters/shinchoku       進捗マスタ作成
❌ GET    /api/masters/sagyou-kubun    作業区分マスタ一覧
❌ POST   /api/masters/sagyou-kubun    作業区分マスタ作成
❌ GET    /api/masters/toiawase        問い合わせマスタ一覧
❌ POST   /api/masters/toiawase        問い合わせマスタ作成
❌ GET    /api/masters/kishu-notes     機種別注意事項一覧
❌ POST   /api/masters/kishu-notes     機種別注意事項作成
```

#### 請求管理API
```
❌ GET    /api/invoices            請求書一覧
❌ POST   /api/invoices/generate   請求書生成
❌ GET    /api/invoices/{id}       請求書詳細
❌ GET    /api/invoices/{id}/pdf   請求書PDF出力
```

#### PDFインポートAPI
```
❌ POST   /api/import/pdf          PDF解析・インポート
❌ GET    /api/import/logs         インポートログ取得
```

#### Drive連携API
```
❌ POST   /api/drive/create-folders     資料フォルダ作成
❌ GET    /api/drive/folders/{project_id} フォルダ情報取得
```

---

## 🚀 実装優先順位

### Phase 1: 基盤強化（1-2週間）
1. **マスタ管理機能の実装**
   - 担当者マスタ
   - 進捗マスタ
   - 作業区分マスタ
   - 問い合わせマスタ

2. **案件管理の強化**
   - 案件詳細画面
   - 全項目対応
   - 担当者専用ビュー

3. **認証の強化**
   - ユーザーロール
   - セッション管理

### Phase 2: 工数管理強化（1-2週間）
4. **工数入力UI改善**
   - カレンダーUI
   - 土日祝日表示

5. **工数集計機能**
   - 担当者別集計
   - 月別集計
   - 作業区分別集計

### Phase 3: 請求・PDF機能（2-3週間）
6. **請求管理機能**
   - 請求書生成
   - PDF出力

7. **PDF自動取り込み**
   - OCR処理
   - データ解析
   - バッチインポート

### Phase 4: Drive連携・高度機能（2週間）
8. **Google Drive連携**
   - フォルダ自動生成
   - 顧客用管理表連携

9. **通知機能**
   - 期限リマインダー
   - 担当者通知

### Phase 5: 最適化・運用機能（1週間）
10. **色分け・UI強化**
11. **バックアップ機能**
12. **エクスポート機能**

---

## 📝 非機能要件

### パフォーマンス
- API応答時間: 500ms以内
- 同時接続ユーザー数: 50人
- データベースクエリ最適化

### セキュリティ
- JWT認証
- パスワードハッシュ化（bcrypt）
- XSS・CSRF対策
- SQLインジェクション対策

### 可用性
- 稼働率: 99%以上
- バックアップ: 日次自動バックアップ
- データ保持期間: 3年

### ユーザビリティ
- レスポンシブデザイン
- モバイル対応
- 操作マニュアル整備

---

## 🔄 移行計画

### 移行ステップ
1. **並行運用期間（1ヶ月）**
   - 既存GASシステムと新システムを並行運用
   - データ整合性チェック

2. **段階的移行**
   - Phase 1完了後: マスタデータ移行
   - Phase 2完了後: 工数データ移行
   - Phase 3完了後: 請求データ移行

3. **完全移行**
   - 全機能テスト完了後
   - ユーザートレーニング実施
   - GASシステムのバックアップ保管

### データ移行
- スプレッドシートからPostgreSQLへのマイグレーション
- マスタデータの整合性チェック
- 工数データの変換・検証

---

## 📚 参考資料

- [既存GASリポジトリ](https://github.com/ACSshiga/my-gas-spreadsheet-script-nissei)
- アップロード済みファイル:
  - `docs/2025-9-22.pdf` - 委託書サンプル
  - `docs/テストシート.xlsx` - 既存工数管理シート
  - `docs/請求書.xlsx` - 請求書フォーマット
  - `docs/資料作成注意点一覧.xlsx` - 機種別注意事項（49項目）

---

**作成日**: 2025-09-30
**最終更新**: 2025-09-30
**バージョン**: 1.0