# AI Rules - 開発ガイドライン（2層構造版）

このディレクトリには、開発ガイドラインが格納されています。

**最終更新**: 2025-10-02

---

## 📁 ディレクトリ構造

```
ai-rules/
├── common/                     # プロジェクト横断（汎用ガイドライン）
│   ├── WORKFLOW.md             # 汎用ワークフロー ⭐ NEW
│   ├── PHASE_MANAGEMENT.md     # フェーズ管理 ⭐ NEW
│   ├── DOCUMENTATION_GUIDE.md  # ドキュメント管理 ⭐ NEW
│   ├── COMMIT_GUIDELINES.md    # コミット規約
│   ├── NAMING_CONVENTIONS.md   # 命名規則
│   ├── ISSUE_GUIDELINES.md     # Issue作成
│   └── PR_PROCESS.md           # PR & レビュー（汎用版）
│
├── nissei/                     # nissei 専用（プロジェクト固有設定）
│   ├── WORKFLOW.md             # 開発ワークフロー（更新済み）
│   ├── SETUP_AND_MCP.md        # 環境構築 & MCP
│   ├── TESTING.md              # テスト
│   ├── DOCUMENTATION_GUIDE.md  # ドキュメント管理（nissei固有）
│   └── PR_AND_REVIEW.md        # PR & レビュー
│
└── README.md                   # このファイル
```

---

## 🌍 common/ - プロジェクト横断（汎用ガイドライン）

**用途**: 複数プロジェクトで共通利用可能な汎用ルール

**特徴**:
- ✅ プロジェクト固有の情報を含まない
- ✅ 他プロジェクトにコピーして利用可能
- ✅ 普遍的なベストプラクティス

### ファイル一覧

**[WORKFLOW.md](./common/WORKFLOW.md)** - 汎用ワークフロー ⭐ NEW
- セッション開始→実装→PR→マージ→ドキュメント更新の基本フロー
- Serenaメモリ読み込み手順
- フェーズ管理との連携

**[PHASE_MANAGEMENT.md](./common/PHASE_MANAGEMENT.md)** - フェーズ管理 ⭐ NEW
- フェーズ定義と進行フロー
- フェーズ開始時・完了時の仕様確認
- PHASES.md と phase_progress.md の管理

**[DOCUMENTATION_GUIDE.md](./common/DOCUMENTATION_GUIDE.md)** - ドキュメント管理 ⭐ NEW
- docs/ と .serena/memories/ の2層構造
- マージ後の更新フロー（両方必須）
- Serenaメモリ操作方法

**[COMMIT_GUIDELINES.md](./common/COMMIT_GUIDELINES.md)** - コミットメッセージガイドライン
- コミットメッセージの形式（type, subject, body）
- コミット前の確認事項

**[NAMING_CONVENTIONS.md](./common/NAMING_CONVENTIONS.md)** - 命名規則
- ファイル・ディレクトリ命名
- 変数・関数命名
- APIエンドポイント命名
- データベーステーブル・カラム命名
- 環境変数命名

**[ISSUE_GUIDELINES.md](./common/ISSUE_GUIDELINES.md)** - Issue作成ガイドライン
- Issueテンプレート（バグ報告、新機能追加、リファクタリング）
- ラベル分類と優先度設定
- Issue作成手順・管理ルール

**[PR_PROCESS.md](./common/PR_PROCESS.md)** - PR & レビューガイド（汎用版）
- PR作成テンプレート
- レビュープロセス
- マージ手順

---

## 🏢 nissei/ - nissei プロジェクト専用

**用途**: nissei プロジェクト固有の設定・ワークフロー

**特徴**:
- ✅ ポート番号（3000, 8000）等の具体的な設定
- ✅ テストユーザー情報
- ✅ Serenaメモリ定義（7個）
- ✅ code-reviewer サブエージェント設定

### ファイル一覧

**[WORKFLOW.md](./nissei/WORKFLOW.md)** - 開発ワークフロー ⭐ 最重要
- 作業開始から終了までの流れ
- セッション開始時のSerenaメモリ読み込み
- 各フェーズへのリンク集

**[SETUP_AND_MCP.md](./nissei/SETUP_AND_MCP.md)** - 環境構築 & MCP サーバー運用 ⭐ 必読
- 環境構築手順（ポート設定・環境変数）
- **Serena MCP**: メモリ機能・コード構造解析・効率的な検索（最重要）
- context7, playwright, github, desktop-commander, supabase

**[TESTING.md](./nissei/TESTING.md)** - テストガイドライン
- E2Eテスト実施手順（Playwright MCP使用）
- テストユーザー情報
- ポート管理・環境クリーンアップ

**[DOCUMENTATION_GUIDE.md](./nissei/DOCUMENTATION_GUIDE.md)** - ドキュメント管理ガイド ⭐ 必読
- **Serena vs docs の使い分け**: AI用詳細仕様 vs 人間用簡潔ドキュメント
- **追記・更新のフロー**: セッション開始時・開発中・PR作成時・マージ後
- **Serenaメモリ一覧**: 7個のメモリファイルの役割と更新タイミング

**[PR_AND_REVIEW.md](./nissei/PR_AND_REVIEW.md)** - PR & レビュー（nissei 専用） ⭐ 最重要
- **code-reviewer サブエージェント レビュー**: レビュー依頼方法・観点・結果分類
- **修正対応**: 修正手順・再レビュー・Issue作成
- **マージ実行**: マージ条件・マージ方法
- **docs/ 更新確認**: 更新対象・更新フロー

---

## 🚀 クイックスタート（nissei プロジェクト）

### 新規セッション開始時（最重要）

⚠️ **毎回必ず実施**: Serenaメモリから前回の状態を読み込む

```
1. mcp__serena__activate_project
   project: "nissei"

2. mcp__serena__list_memories
   → 利用可能なメモリを確認

3. mcp__serena__read_memory
   memory_file_name: "current_issues_and_priorities.md"
   → 現在の優先度を把握

4. mcp__serena__read_memory
   memory_file_name: "phase_progress.md"  # フェーズ管理時
   → 現在のフェーズ・進捗を確認

5. フェーズ・仕様確認
   - 現在のフェーズと実装内容を確認
   - 不明点はユーザーに質問

6. 作業開始
```

詳細: [nissei/SETUP_AND_MCP.md](./nissei/SETUP_AND_MCP.md) の「Serena MCP」セクション、[common/PHASE_MANAGEMENT.md](./common/PHASE_MANAGEMENT.md)

### 新規タスクを開始する場合

1. [common/WORKFLOW.md](./common/WORKFLOW.md) で基本フローを把握
2. [nissei/WORKFLOW.md](./nissei/WORKFLOW.md) でnissei固有の手順を確認
3. ブランチを作成（`feat-*`, `fix-*`）
4. 実装・修正を行う（[common/NAMING_CONVENTIONS.md](./common/NAMING_CONVENTIONS.md) 準拠）
5. [nissei/TESTING.md](./nissei/TESTING.md) に従ってE2Eテストを実施
6. [common/COMMIT_GUIDELINES.md](./common/COMMIT_GUIDELINES.md) に従ってコミット
7. [nissei/PR_AND_REVIEW.md](./nissei/PR_AND_REVIEW.md) に従ってPR作成・レビュー・マージ
8. **docs/ と Serenaメモリの両方を更新**（[common/DOCUMENTATION_GUIDE.md](./common/DOCUMENTATION_GUIDE.md)）
9. フェーズ完了時は仕様確認（[common/PHASE_MANAGEMENT.md](./common/PHASE_MANAGEMENT.md)）

---

## 🔗 ドキュメント間の関係

```
common/WORKFLOW.md（汎用）⭐ 基本フロー
    ├── common/PHASE_MANAGEMENT.md（フェーズ管理）⭐ NEW
    │   ├── docs/PHASES.md（人間用フェーズ一覧）
    │   └── .serena/memories/phase_progress.md（AI用進捗）
    │
    └── common/DOCUMENTATION_GUIDE.md（ドキュメント管理）⭐ NEW
        ├── docs/（人間用簡潔版）
        └── .serena/memories/（AI用詳細版）

nissei/WORKFLOW.md（nissei 専用）⭐ 最重要
    │
    ├── SETUP_AND_MCP.md（nissei 専用）
    │   ├── Serena MCP（メモリ機能・セッション開始時必須）
    │   └── nissei/DOCUMENTATION_GUIDE.md（nissei固有のドキュメント）
    │
    ├── common/NAMING_CONVENTIONS.md（汎用）
    │
    ├── TESTING.md（nissei 専用）
    │   └── Playwright MCP（E2Eテスト）
    │
    ├── common/COMMIT_GUIDELINES.md（汎用）
    │
    ├── PR_AND_REVIEW.md（nissei 専用）⭐ 最重要
    │   ├── common/PR_PROCESS.md（汎用版の参照）
    │   ├── code-reviewer サブエージェント（レビュー）
    │   ├── common/DOCUMENTATION_GUIDE.md（docs更新確認）
    │   └── common/ISSUE_GUIDELINES.md（Issue作成）
    │
    └── common/PHASE_MANAGEMENT.md（フェーズ完了確認）
```

---

## 🎯 2層構造の目的

### なぜ分離したのか

1. **再利用性の向上**: `common/` の内容は他プロジェクトでそのまま使用可能
2. **保守性の向上**: 汎用ルール変更時は `common/` のみ修正すれば良い
3. **明確な責任分離**: どこに何を書くべきかが明確

### どちらに書くべきか

#### common/ に書くべき内容
- ✅ 汎用ワークフロー（基本フロー）
- ✅ フェーズ管理（フェーズ進行ルール）
- ✅ ドキュメント管理（docs/ と Serenaメモリの使い分け）
- ✅ コミットメッセージの形式
- ✅ 命名規則（言語・フレームワーク共通）
- ✅ PR作成プロセス
- ✅ Issue管理ルール

#### nissei/ に書くべき内容
- ✅ nissei固有のワークフロー（ポート・テストユーザー等）
- ✅ ポート番号（3000, 8000）
- ✅ テストユーザー情報
- ✅ Serenaメモリ定義（8個）
- ✅ code-reviewerサブエージェント設定

---

## ⚠️ 重要な注意事項

- ✅ **セッション開始時にSerenaメモリから状況を把握**（phase_progress.md含む）
- ✅ **フェーズ開始時に必ず仕様確認**（ユーザーと合意）
- ✅ **mainブランチへの直接作業は絶対禁止**
- ✅ **コミット前に必ず動作確認とE2Eテストを実施**
- ✅ **PR作成直後に必ずcode-reviewer サブエージェント レビューを依頼**
- ✅ **Critical問題が存在する場合は絶対にマージしない**
- ✅ **PR作成→レビュー→マージ→ドキュメント更新までを1セット**（PRを溜めない）
- ✅ **マージ後は docs/ と Serenaメモリの両方を更新**（必須）
- ✅ **フェーズ完了時に必ず仕様との整合性確認**（ユーザーと最終確認）
- ✅ **機密情報（APIキー、パスワード等）はコミットしない**

---

## 🔗 外部ドキュメント

### プロジェクト設定

- **[../CLAUDE.md](../CLAUDE.md)**: Claude Code 設定と全体ルール

### 人間用ドキュメント（簡潔版）

- **[../docs/README.md](../docs/README.md)**: プロジェクト概要
- **[../docs/SETUP.md](../docs/SETUP.md)**: 環境構築手順
- **[../docs/DATABASE.md](../docs/DATABASE.md)**: データベース設計（簡潔版）
- **[../docs/API.md](../docs/API.md)**: API仕様（簡潔版）

### AI用ドキュメント（詳細版）

詳細な技術仕様は `.serena/memories/` を参照：
- `database_specifications.md` - DB詳細仕様（CREATE TABLE文等）
- `api_specifications.md` - API詳細仕様（全エンドポイント）
- `system_architecture.md` - システムアーキテクチャ詳細
- `implementation_status.md` - 実装状況・進捗
- `current_issues_and_priorities.md` - 現在の課題・優先度（最重要）

参考: [nissei/DOCUMENTATION_GUIDE.md](./nissei/DOCUMENTATION_GUIDE.md)

---

## 📝 更新履歴

- **2025-10-02 (4回目)**: フェーズ管理とドキュメント更新フローの追加
  - **common/WORKFLOW.md** 新規作成: 汎用ワークフロー定義
  - **common/PHASE_MANAGEMENT.md** 新規作成: フェーズ管理ガイド
  - **common/DOCUMENTATION_GUIDE.md** 新規作成: docs/ と Serenaメモリの2層管理
  - **nissei/WORKFLOW.md** 更新: フェーズ管理とドキュメント更新フローを追加
  - **CLAUDE.md** 更新: フェーズ管理フローとSerenaメモリ更新を明記
  - README.md（このファイル）更新: 新規ガイドラインを反映

- **2025-10-02 (3回目)**: 2層構造への分離
  - **common/** フォルダ作成: プロジェクト横断的な汎用ガイドライン
  - **nissei/** フォルダ作成: nissei プロジェクト固有の設定
  - 各ファイルに「プロジェクト横断」「プロジェクト固有」ヘッダー追加
  - README.md を全面改訂（2層構造の説明追加）
  - 再利用性・保守性・明確な責任分離を実現

- **2025-10-02 (2回目)**: ドキュメント管理ガイド追加
  - **nissei/DOCUMENTATION_GUIDE.md** を新規作成
  - Serena vs docs の使い分けを明確化（AI詳細 vs 人間簡潔）
  - 追記・更新のフローを定義

- **2025-10-02**: MECE整理・統合を実施
  - PR関連3ファイルを **PR_AND_REVIEW.md** に統合
  - MCP関連2ファイルを **SETUP_AND_MCP.md** に統合
  - 11ファイル → 8ファイルに削減（-27%）

- **2025-10-01**: 全ドキュメントを整理・統合
  - code-reviewer サブエージェント による実際のレビューフローに合わせて更新
  - README.md（このファイル）を新規作成
