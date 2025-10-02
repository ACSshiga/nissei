# 資料管理・注意点リスト仕様（2025-10-02確定）

**最終更新**: 2025-10-02
**バージョン**: v2.0

## 📚 資料管理システム

### 機種の定義

**機種 = シリーズ + トン数 + 世代**

例:
- `NEX140Ⅲ` ← これが機種
- `NEX140Ⅲ-24AK` ← 機種 + 仕様コード

仕様コード（-24AK）は案件ごとの個別仕様であり、機種マスタには含まれない。

---

### ファイルストレージ

**開発環境**: MinIO（Docker Compose）
**本番環境**: Supabase Storage

**理由**:
- Supabaseは既存システムと統合しやすい
- コストが安い（月100円〜500円程度）
- 管理画面で確認できる

**バケット名**: `materials`

---

### 資料の4段階共有スコープ

| Scope | 説明 | 例 |
|-------|------|---|
| `machine` | 案件固有（機番） | G40125004 |
| `model` | 機種全体（STD資料） | NEX140Ⅲ |
| `tonnage` | トン数帯 | NEX 140t |
| `series` | シリーズ | NEXシリーズ |

---

### データベース設計

#### materials（資料テーブル）

```sql
CREATE TABLE materials (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  title VARCHAR(200) NOT NULL,
  machine_no VARCHAR(100),
  model VARCHAR(100),
  scope VARCHAR(20) NOT NULL,
  series VARCHAR(50) NOT NULL,
  tonnage INTEGER,
  file_path VARCHAR(500) NOT NULL,
  file_size BIGINT,
  uploaded_by UUID REFERENCES users(id) ON DELETE SET NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX idx_materials_scope ON materials(scope);
CREATE INDEX idx_materials_machine_no ON materials(machine_no);
CREATE INDEX idx_materials_model ON materials(model);
CREATE INDEX idx_materials_series_tonnage ON materials(series, tonnage);
```

**COMMENT**:
- `scope`: スコープレベル: machine, model, tonnage, series
- `machine_no`: 特定機番（scope=machineの場合）
- `model`: 特定機種（scope=modelの場合）
- `series`: シリーズ名（NEX, HMX等）
- `tonnage`: トン数（scope=tonnageの場合）

**重要**: 資料カテゴリ（A板、B板、シーケンサ等）は不要。注意点リストにのみカテゴリが必要。

---

### 画面構成

#### 1. 案件の資料フォルダ（案件画面から）

**アクセス**: 案件一覧の [📁資料] ボタン

**アップロード**: 
- 複数ファイル対応（ドラッグ&ドロップ）
- 自動的に `scope = 'machine'` として保存

**表示**:
```
━━━ 📋 この案件の資料 (3件) ━━━
📄 図面_rev1.pdf           2025/01/15  [編集] [削除]

━━━ 📚 STD資料（機種: HMX7） (2件) ━━━
📄 HMX7標準仕様書.pdf       2024/12/01  [編集] [削除]

━━━ 📚 共通資料（トン数帯: HMX 7t） (1件) ━━━
📄 7t共通図面.pdf           2024/10/01  [編集] [削除]

━━━ 📚 共通資料（シリーズ: HMXシリーズ） (1件) ━━━
📄 HMXシリーズカタログ.pdf   2024/09/01  [編集] [削除]
```

---

#### 2. 機種別資料管理（サイドバーから）

**アクセス**: サイドバー > 資料管理

**階層的アップロード**: シリーズ → トン数 → 世代（機種）の順で絞り込み

**下位階層は省略可能**:
- シリーズのみ選択 → `scope = 'series'`
- シリーズ + トン数 → `scope = 'tonnage'`
- シリーズ + トン数 + 世代 → `scope = 'model'`

```
資料管理 > 機種別資料

┌─────────────────────────────────────────────┐
│ シリーズを選択: [NEX ▼]                       │
│ トン数を選択:   [140 ▼]  ← 任意（スキップ可） │
│ 世代を選択:     [Ⅲ ▼]    ← 任意（スキップ可） │
└─────────────────────────────────────────────┘

[📤 ファイルを選択] または ドラッグ&ドロップ
```

---

### 資料編集機能

**機能**: アップロード後にscope変更可能

**編集モーダル**:
```
┌─ 資料を編集 ────────────────────────┐
│ ファイル名: 図面_rev1.pdf             │
│ タイトル: [図面_rev1           ]     │
│                                      │
│ この資料の共有範囲:                   │
│ ◉ この案件のみ (機番: G40125004)     │
│ ○ この機種全体 (HMX7)                │
│ ○ このトン数帯 (HMX 7t)              │
│ ○ このシリーズ (HMXシリーズ)          │
│                                      │
│         [キャンセル]  [保存]          │
└──────────────────────────────────────┘
```

---

### 複数ファイル一括アップロード

**仕様**:
- ブラウザ標準の `<input type="file" multiple>`
- ドラッグ&ドロップ対応
- アップロード前にファイル一覧を表示
- 「すべてアップロード」ボタンで一括処理

---

## 📋 注意点リストシステム

### 概要

**重要**: チェックリスト機能は削除。注意点リスト機能のみ実装。

現行の「資料作成注意点一覧.csv」をシステム化。

---

### データベース設計

#### master_chuiten_category（注意点カテゴリマスタ）

```sql
CREATE TABLE master_chuiten_category (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(100) UNIQUE NOT NULL,  -- A板, B板, シーケンサ, etc
  sort_order INTEGER DEFAULT 0,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 初期データ
INSERT INTO master_chuiten_category (name, sort_order) VALUES
  ('A板', 1),
  ('B板', 2),
  ('C板', 3),
  ('D板', 4),
  ('シーケンサ', 5),
  ('シーケンサ・A板', 6),
  ('アンプBOX', 7),
  ('制御BOXカバーA', 8),
  ('回路図', 9),
  ('端子台', 10),
  ('その他', 99);
```

---

#### master_chuiten（注意点マスタ）

```sql
CREATE TABLE master_chuiten (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  seq_no INTEGER UNIQUE NOT NULL,               -- 連番 (1, 2, 3...) ⚠️ UNIQUE制約
  target_series VARCHAR(100),                   -- 対象シリーズ: 'TNX', 'FNX', etc
  target_model_pattern VARCHAR(100),            -- 対象機種パターン: 'TC15～', 'NEX30'
  category_id UUID REFERENCES master_chuiten_category(id),
  note TEXT NOT NULL,                           -- 注意点・留意点
  author VARCHAR(100),                          -- 記入者
  remarks TEXT,                                 -- 備考
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_chuiten_series ON master_chuiten(target_series);
CREATE INDEX idx_chuiten_category ON master_chuiten(category_id);
```

**注意**: 
- `seq_no`にUNIQUE制約があるため、連番変更時は重複に注意
- PATCH更新でseq_noを変更可能（重複チェックあり）

---

### 画面構成

#### 1. 注意点一覧画面

**フィルタ機能**:
- シリーズ
- カテゴリ
- キーワード検索

```
注意点リスト

┌─ フィルタ ────────────────────────┐
│ シリーズ: [TNX ▼]                  │
│ カテゴリ:   [シーケンサ ▼]         │
│ キーワード: [端子台        ] [🔍]  │
└──────────────────────────────────┘

検索結果 (5件)

┌──────────────────────────────────┐
│ #1 | TNX | シーケンサ・A板         │
│ 自動機の端子出し...               │
│ 記入者: - | 備考: -               │
├──────────────────────────────────┤
│ #3 | TNX | A板                    │
│ 端子台が2個つくA板...             │
│ 記入者: 藤沢 | 備考: -            │
└──────────────────────────────────┘

[+ 新規追加] [編集] [削除]
```

---

#### 2. 案件詳細の注意点タブ

**機能**: 案件の機種に関連する注意点を自動表示

**シリーズ抽出ロジック**: 
- 案件の機種（model）から正規表現で先頭の英字部分を抽出
- 例: `NEX140Ⅲ-24AK` → `NEX`

```
案件詳細 > TC1025006 TNX100RⅢ18V

[基本情報] [工数入力] [資料] [注意点] ← NEW

関連する注意点 (3件)

┌──────────────────────────────────┐
│ #1 | TNX | シーケンサ・A板         │
│ 自動機の端子出し...               │
└──────────────────────────────────┘
```

---

## 🗂️ マスタデータ

### master_work_category（作業区分マスタ）

```sql
CREATE TABLE master_work_category (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(100) UNIQUE NOT NULL,  -- 盤配, 線加工
  sort_order INTEGER DEFAULT 0,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 初期データ
INSERT INTO master_work_category (name, sort_order) VALUES
  ('盤配', 1),
  ('線加工', 2);
```

---

### master_kishyu（機種マスタ）

```sql
CREATE TABLE master_kishyu (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  model VARCHAR(100) UNIQUE NOT NULL,  -- 機種名: NEX140Ⅲ
  series VARCHAR(50) NOT NULL,         -- シリーズ: NEX
  tonnage INTEGER NOT NULL,            -- トン数: 140
  generation VARCHAR(10) NOT NULL,     -- 世代: Ⅲ
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_kishyu_series ON master_kishyu(series);
CREATE INDEX idx_kishyu_tonnage ON master_kishyu(series, tonnage);
```

**注**: 仕様コードは含まない

---

### master_nounyusaki（納入先マスタ）

```sql
CREATE TABLE master_nounyusaki (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(100) UNIQUE NOT NULL,  -- 例: A社、B社
  code VARCHAR(50),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**自動追加**: PDF取り込み時に新しい納入先を自動マスタ化

---

### master_shinchoku（進捗マスタ）

```sql
CREATE TABLE master_shinchoku (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(100) NOT NULL,           -- 例: 未着手、作図中、完成(A社)
  code VARCHAR(50) UNIQUE NOT NULL,
  background_color VARCHAR(7),          -- 背景色（例: #FF0000）
  is_completed BOOLEAN DEFAULT false,   -- 完了フラグ（請求書生成用）
  sort_order INTEGER DEFAULT 0,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 📄 案件テーブルの追加フィールド

```sql
ALTER TABLE projects ADD COLUMN reference_code VARCHAR(200);      -- 参考製番
ALTER TABLE projects ADD COLUMN circuit_diagram_no VARCHAR(200);  -- 回路図番
ALTER TABLE projects ADD COLUMN delay_reason TEXT;                -- 係り超過理由
```

---

## 📜 請求書仕様

### 年月管理

**UNIQUE制約**: `(year, month)` で請求書を管理

```sql
CREATE TABLE invoices (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  year INTEGER NOT NULL,
  month INTEGER NOT NULL CHECK (month BETWEEN 1 AND 12),
  status VARCHAR(20) DEFAULT 'draft' NOT NULL,
  closed_at TIMESTAMP,
  closed_by UUID REFERENCES users(id) ON DELETE SET NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
  UNIQUE(year, month)
);
```

**ステータス**: `draft` | `closed`

---

### 出力項目（確定）

CSV形式（BOM付きUTF-8）:
- 管理No
- 委託業務内容（機番）
- 実工数（時間）

**それ以外の項目は不要**（納入先、作業区分、担当者等は含まない）

**工数集計**: `work_logs`テーブルから指定年月の工数を自動集計（プロジェクト別）

---

## 🔧 実装優先順位

### Phase 1: 基盤（✅ 完了）
1. ✅ マスタ管理画面（進捗、作業区分、注意点カテゴリ、機種マスタ）
2. ✅ 全体管理画面（案件一覧）
3. ✅ 工数入力グリッド
4. ✅ 資料管理機能（Supabase Storage連携）
5. ✅ 注意点リスト機能
6. ✅ 請求書生成

### Phase 2: フロントエンド実装・品質向上（🟡 次フェーズ）
7. フロントエンド画面実装
8. PDF自動取り込み
9. E2Eテスト・品質改善

---

## 📝 メモ

- **製番の範囲指定による注意点適用ルール**: 不要（削除）
- **ベースコード（参考資料）の記録機能**: 不要（削除）
- **チェックリスト機能**: 削除（注意点リストのみ実装）
- **資料カテゴリ**: 不要（注意点リストにのみカテゴリが必要）
- **シリーズ抽出**: 正規表現 `^([A-Za-z]+)` で機種名から自動抽出
