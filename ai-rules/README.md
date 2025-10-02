# AI Rules - 開発ガイドライン（2層構造版）

このディレクトリには、開発ガイドラインが格納されています。

**最終更新**: 2025-10-02

---

## 📁 ディレクトリ構造

```
ai-rules/
├── common/              # プロジェクト横断（汎用ガイドライン）
│   ├── COMMIT_GUIDELINES.md
│   ├── NAMING_CONVENTIONS.md
│   ├── ISSUE_GUIDELINES.md
│   └── PR_PROCESS.md
│
├── nissei/              # nissei 専用（プロジェクト固有設定）
│   ├── WORKFLOW.md
│   ├── SETUP_AND_MCP.md
│   ├── TESTING.md
│   ├── DOCUMENTATION_GUIDE.md
│   └── PR_AND_REVIEW.md
│
└── README.md            # このファイル
```

---

## 🌍 common/ - プロジェクト横断（汎用ガイドライン）

**用途**: 複数プロジェクトで共通利用可能な汎用ルール

**特徴**:
- ✅ プロジェクト固有の情報を含まない
- ✅ 他プロジェクトにコピーして利用可能
- ✅ 普遍的なベストプラクティス

### ファイル一覧

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

4. 作業開始
```

詳細: [nissei/SETUP_AND_MCP.md](./nissei/SETUP_AND_MCP.md) の「Serena MCP」セクション

### 新規タスクを開始する場合

1. [nissei/WORKFLOW.md](./nissei/WORKFLOW.md) を読んで全体の流れを把握
2. ブランチを作成（`feat-*`, `fix-*`）
3. 実装・修正を行う（[common/NAMING_CONVENTIONS.md](./common/NAMING_CONVENTIONS.md) 準拠）
4. [nissei/TESTING.md](./nissei/TESTING.md) に従ってE2Eテストを実施
5. [common/COMMIT_GUIDELINES.md](./common/COMMIT_GUIDELINES.md) に従ってコミット
6. [nissei/PR_AND_REVIEW.md](./nissei/PR_AND_REVIEW.md) に従ってPR作成・レビュー・マージ
7. docs/ の更新が必要か確認・更新
8. 重要な情報をSerenaメモリに保存

---

## 🔗 ドキュメント間の関係

```
WORKFLOW.md（nissei 専用）⭐ 最重要
    │
    ├── SETUP_AND_MCP.md（nissei 専用）
    │   ├── Serena MCP（メモリ機能・セッション開始時必須）
    │   └── DOCUMENTATION_GUIDE.md（Serena/docs使い分け）⭐ 必読
    │
    ├── NAMING_CONVENTIONS.md（汎用）
    │
    ├── TESTING.md（nissei 専用）
    │   └── Playwright MCP（E2Eテスト）
    │
    ├── COMMIT_GUIDELINES.md（汎用）
    │
    ├── PR_AND_REVIEW.md（nissei 専用）⭐ 最重要
    │   ├── PR_PROCESS.md（汎用版の参照）
    │   ├── code-reviewer サブエージェント（レビュー）
    │   ├── DOCUMENTATION_GUIDE.md（docs更新確認）
    │   └── ISSUE_GUIDELINES.md（Issue作成）
    │
    └── ISSUE_GUIDELINES.md（汎用）
```

---

## 🎯 2層構造の目的

### なぜ分離したのか

1. **再利用性の向上**: `common/` の内容は他プロジェクトでそのまま使用可能
2. **保守性の向上**: 汎用ルール変更時は `common/` のみ修正すれば良い
3. **明確な責任分離**: どこに何を書くべきかが明確

### どちらに書くべきか

#### common/ に書くべき内容
- ✅ コミットメッセージの形式
- ✅ 命名規則（言語・フレームワーク共通）
- ✅ PR作成プロセス
- ✅ Issue管理ルール

#### nissei/ に書くべき内容
- ✅ ポート番号（3000, 8000）
- ✅ テストユーザー情報
- ✅ Serenaメモリ定義
- ✅ プロジェクト固有のワークフロー

---

## ⚠️ 重要な注意事項

- ✅ **毎セッション開始時にSerenaメモリから状況を把握する**（最重要）
- ✅ **mainブランチへの直接作業は絶対禁止**
- ✅ **コミット前に必ず動作確認とE2Eテストを実施**
- ✅ **PR作成直後に必ずcode-reviewer サブエージェント レビューを依頼**
- ✅ **Critical問題が存在する場合は絶対にマージしない**
- ✅ **PR作成→レビュー→マージまでを1セットの作業として完了させる**（PRを溜めない）
- ✅ **マージ後は必ず docs/ の更新が必要か確認する**
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

- **2025-10-02 (3回目)**: 2層構造への分離
  - **common/** フォルダ作成: プロジェクト横断的な汎用ガイドライン
  - **nissei/** フォルダ作成: nissei プロジェクト固有の設定
  - 各ファイルに「プロジェクト横断」「プロジェクト固有」ヘッダー追加
  - README.md を全面改訂（2層構造の説明追加）
  - 再利用性・保守性・明確な責任分離を実現

- **2025-10-02 (2回目)**: ドキュメント管理ガイド追加
  - **DOCUMENTATION_GUIDE.md** を新規作成
  - Serena vs docs の使い分けを明確化（AI詳細 vs 人間簡潔）
  - 追記・更新のフローを定義

- **2025-10-02**: MECE整理・統合を実施
  - PR関連3ファイルを **PR_AND_REVIEW.md** に統合
  - MCP関連2ファイルを **SETUP_AND_MCP.md** に統合
  - 11ファイル → 8ファイルに削減（-27%）

- **2025-10-01**: 全ドキュメントを整理・統合
  - code-reviewer サブエージェント による実際のレビューフローに合わせて更新
  - README.md（このファイル）を新規作成
