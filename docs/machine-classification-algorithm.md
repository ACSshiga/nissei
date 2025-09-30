# 機種分類アルゴリズム設計書

**作成日**: 2025-09-30
**目的**: 機種名（例: FNX140Ⅳ-36AK, NEX80Ⅴ-5E）から属性を自動抽出し分類する

---

## 📊 分類対象の属性

### 抽出項目
1. **シリーズ名** (series): NEX, FNX, TNS, HMX など
2. **トン数** (tonnage): 80, 140, 250 など（数値）
3. **世代** (generation): Ⅳ, Ⅴ など（ローマ数字）
4. **仕様コード** (spec_code): 36AK, 5E など

### 特殊カテゴリ
- **H0**: 特殊カテゴリ
- **B板**: 特殊カテゴリ
- **その他**: 未分類

---

## 🔍 正規表現パターン

### パターン1: 標準形式
```python
# 例: FNX140Ⅳ-36AK, NEX80Ⅴ-5E
pattern = r"^([A-Z]+)(\d+)?([ⅠⅡⅢⅣⅤⅥⅦⅧⅨⅩiivxIIVX]*)-?(.*)$"

# グループ分解:
# group(1): シリーズ名 (FNX, NEX)
# group(2): トン数 (140, 80)
# group(3): 世代 (Ⅳ, Ⅴ)
# group(4): 仕様コード (36AK, 5E)
```

### パターン2: 特殊カテゴリ
```python
# H0, B板 などの特殊ケース
special_patterns = {
    r"^H0": "H0",
    r"B板": "B板",
}
```

### 世代正規化
```python
# 半角・全角・大文字・小文字を統一
generation_map = {
    "I": "Ⅰ", "i": "Ⅰ", "1": "Ⅰ",
    "II": "Ⅱ", "ii": "Ⅱ", "2": "Ⅱ",
    "III": "Ⅲ", "iii": "Ⅲ", "3": "Ⅲ",
    "IV": "Ⅳ", "iv": "Ⅳ", "4": "Ⅳ",
    "V": "Ⅴ", "v": "Ⅴ", "5": "Ⅴ",
    # ... 以降も同様
}
```

---

## 💾 データモデル

### テーブル追加: `machine_series_master`

```sql
CREATE TABLE machine_series_master (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  series_name VARCHAR(50) NOT NULL UNIQUE,  -- NEX, FNX など
  display_name VARCHAR(100) NOT NULL,        -- 表示名
  description TEXT,                          -- 説明
  category VARCHAR(50),                      -- カテゴリ（標準/特殊）
  checklist_template_category VARCHAR(50),  -- 注意点テンプレート紐付け
  sort_order INTEGER DEFAULT 0,
  is_active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- 初期データ例
INSERT INTO machine_series_master (series_name, display_name, category) VALUES
  ('NEX', 'NEXシリーズ', '標準'),
  ('FNX', 'FNXシリーズ', '標準'),
  ('TNS', 'TNSシリーズ', '標準'),
  ('HMX', 'HMXシリーズ', '標準'),
  ('H0', 'H0シリーズ', '特殊'),
  ('B板', 'B板', '特殊');
```

### `projects` テーブル拡張

```sql
ALTER TABLE projects ADD COLUMN series_name VARCHAR(50);
ALTER TABLE projects ADD COLUMN tonnage INTEGER;
ALTER TABLE projects ADD COLUMN generation VARCHAR(10);
ALTER TABLE projects ADD COLUMN spec_code VARCHAR(50);
ALTER TABLE projects ADD COLUMN classification_status VARCHAR(20) DEFAULT 'auto';
-- classification_status: 'auto' (自動分類), 'manual' (手動修正), 'unclassified' (分類不能)
```

---

## 🛠️ 実装仕様

### Python関数（backend/app/services/machine_classifier.py）

```python
import re
from typing import Optional, Dict

class MachineClassifier:
    """機種名の自動分類サービス"""

    # 標準パターン
    STANDARD_PATTERN = re.compile(
        r"^([A-Z]+)(\d+)?([ⅠⅡⅢⅣⅤⅥⅦⅧⅨⅩiivxIIVX]*)-?(.*)$"
    )

    # 特殊パターン
    SPECIAL_PATTERNS = {
        "H0": re.compile(r"^H0"),
        "B板": re.compile(r"B板"),
    }

    # 世代正規化マップ
    GENERATION_MAP = {
        "I": "Ⅰ", "i": "Ⅰ", "1": "Ⅰ",
        "II": "Ⅱ", "ii": "Ⅱ", "2": "Ⅱ",
        "III": "Ⅲ", "iii": "Ⅲ", "3": "Ⅲ",
        "IV": "Ⅳ", "iv": "Ⅳ", "4": "Ⅳ",
        "V": "Ⅴ", "v": "Ⅴ", "5": "Ⅴ",
        "VI": "Ⅵ", "vi": "Ⅵ", "6": "Ⅵ",
        "VII": "Ⅶ", "vii": "Ⅶ", "7": "Ⅶ",
        "VIII": "Ⅷ", "viii": "Ⅷ", "8": "Ⅷ",
        "IX": "Ⅸ", "ix": "Ⅸ", "9": "Ⅸ",
        "X": "Ⅹ", "x": "Ⅹ", "10": "Ⅹ",
    }

    @classmethod
    def classify(cls, machine_name: str) -> Dict[str, Optional[str]]:
        """
        機種名を自動分類

        Args:
            machine_name: 機種名（例: FNX140Ⅳ-36AK）

        Returns:
            {
                'series_name': 'FNX',
                'tonnage': 140,
                'generation': 'Ⅳ',
                'spec_code': '36AK',
                'classification_status': 'auto'
            }
        """
        if not machine_name:
            return cls._unclassified()

        # 特殊パターンチェック
        for category, pattern in cls.SPECIAL_PATTERNS.items():
            if pattern.search(machine_name):
                return {
                    'series_name': category,
                    'tonnage': None,
                    'generation': None,
                    'spec_code': None,
                    'classification_status': 'auto'
                }

        # 標準パターンマッチ
        match = cls.STANDARD_PATTERN.match(machine_name)
        if not match:
            return cls._unclassified()

        series_name = match.group(1) if match.group(1) else None
        tonnage = int(match.group(2)) if match.group(2) else None
        generation_raw = match.group(3) if match.group(3) else None
        spec_code = match.group(4) if match.group(4) else None

        # 世代正規化
        generation = cls._normalize_generation(generation_raw) if generation_raw else None

        return {
            'series_name': series_name,
            'tonnage': tonnage,
            'generation': generation,
            'spec_code': spec_code,
            'classification_status': 'auto'
        }

    @classmethod
    def _normalize_generation(cls, raw: str) -> str:
        """世代表記を正規化"""
        return cls.GENERATION_MAP.get(raw, raw)

    @classmethod
    def _unclassified(cls) -> Dict[str, Optional[str]]:
        """分類不能の場合"""
        return {
            'series_name': 'その他',
            'tonnage': None,
            'generation': None,
            'spec_code': None,
            'classification_status': 'unclassified'
        }
```

---

## 🧪 テストケース

### 正常系

| 入力 | series_name | tonnage | generation | spec_code |
|------|-------------|---------|------------|-----------|
| FNX140Ⅳ-36AK | FNX | 140 | Ⅳ | 36AK |
| NEX80Ⅴ-5E | NEX | 80 | Ⅴ | 5E |
| TNS250Ⅲ | TNS | 250 | Ⅲ | |
| HMX7-CN2 | HMX | 7 | | CN2 |

### 特殊ケース

| 入力 | series_name | category |
|------|-------------|----------|
| H0-特殊仕様 | H0 | 特殊 |
| B板加工 | B板 | 特殊 |

### 異常系

| 入力 | series_name | classification_status |
|------|-------------|----------------------|
| (空文字) | その他 | unclassified |
| 123ABC | その他 | unclassified |
| 不明機種 | その他 | unclassified |

---

## 🔄 運用フロー

### 1. PDF取込時の自動分類
```python
# PDFから機種名を抽出
machine_name = extract_machine_name_from_pdf(pdf_text)

# 自動分類
classification = MachineClassifier.classify(machine_name)

# DBに保存
project = Project(
    series=machine_name,  # 元の機種名
    series_name=classification['series_name'],
    tonnage=classification['tonnage'],
    generation=classification['generation'],
    spec_code=classification['spec_code'],
    classification_status=classification['classification_status']
)
```

### 2. 手動修正
- 案件詳細画面で分類結果を編集可能
- 編集時に `classification_status` を `'manual'` に変更
- 手動修正後は自動再分類されない

### 3. マスタ追加
- 新しいシリーズが登場したら `machine_series_master` に追加
- 追加後、未分類案件を再分類バッチ実行

---

## 📈 Phase 2 拡張案

### 機械学習による分類精度向上
- 過去の手動修正データを学習
- 類似機種名の推測機能

### 階層的分類
- 大カテゴリ（射出成形機/プレス機など）
- 中カテゴリ（シリーズ）
- 小カテゴリ（世代・トン数）

### 注意点テンプレート自動紐付け
- 分類結果から該当する注意点を自動展開
- 例: series_name="NEX" → チェックリストカテゴリ="NEX"

---

**実装優先度**: Phase 1（MVP必須）
**担当**: Backend開発者
**テスト**: 既存データ（テストシート.xlsx）での分類精度検証