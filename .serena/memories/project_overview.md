# Nissei 工数管理システム - プロジェクト概要

**最終更新**: 2025-10-02

## プロジェクト基本情報

### 目的
既存のGoogle Spreadsheet + Apps Scriptベースの工数管理システムを、FastAPI + Next.jsによるWebアプリケーションに完全移行

### 対象業務
- 設計業務の進捗管理
- 工数入力・集計（15分刻み、案件ごと）
- 委託書PDFからの自動データ取り込み
- 請求書データ生成（Excel出力）
- 資料管理（機種・機番別）
- 資料作成注意点のチェックリスト管理

### 技術スタック

#### フロントエンド
- Next.js 14 (App Router)
- TypeScript
- Tailwind CSS
- SWR（データフェッチング）

#### バックエンド
- FastAPI
- Python 3.11+
- SQLAlchemy（ORM）
- Pydantic（バリデーション）
- JWT認証

#### データベース
- Supabase（PostgreSQL）
- プロジェクトID: wwyrthkizkcgndyorcww

#### インフラ
- Docker + Docker Compose
- ポート設定（固定・変更禁止）:
  - フロントエンド: 3000
  - バックエンド: 8000

## リポジトリ情報

- **リポジトリ名**: nissei
- **Owner**: ShigaRyunosuke10
- **Git remote**: origin

## ワークフロー（重要）

### 業務フロー
1. **PDF取り込み**: 委託書PDF → 案件情報自動読み取り
2. **全体管理画面**: 管理者が案件を確認し、担当者にアサイン
3. **担当者画面**: 各担当者が自分の案件を確認（管理No順）
4. **工数入力**: 作業時間・進捗を入力
5. **請求書生成**: 完了案件から請求データを自動生成

### 開発ワークフロー
1. 専用ブランチ作成（`feat-*`, `fix-*`, `docs-*`）
2. 実装・修正
3. E2Eテスト実施（Playwright MCP）
4. コミット（COMMIT_GUIDELINES.md準拠）
5. PR作成（PR_AND_REVIEW.md準拠）
6. **code-reviewer サブエージェント レビュー**（必須）
7. マージ → docs/ 更新確認

⚠️ **重要**: mainブランチへの直接作業は絶対禁止

## 実装優先順位

### Phase 1: MVP基盤（現在進行中）
1. ✅ マスタ管理機能
2. ⚠️ 案件管理強化（全項目対応 - 仕様確認が必要）
3. ❌ 工数グリッドUI（月グリッド表示・セル編集）

### Phase 2: 自動化・資料管理
4. ❌ PDF自動取り込み
5. ❌ 資料集ハブ
6. ❌ 注意点チェックリスト

### Phase 3: 請求・集計
7. ❌ 請求管理機能
8. ❌ 工数集計・ダッシュボード強化

### Phase 4: 最適化・運用
9. ❌ モバイル対応最適化
10. ❌ 監査ログ・バックアップ

## ディレクトリ構造

```
nissei/
├── CLAUDE.md              # Claude Code設定
├── README.md              # プロジェクト概要
├── .claude/agents/        # カスタムサブエージェント
│   └── code-reviewer.md   # PRレビュー専門エージェント
├── ai-rules/              # AI用汎用ルール
│   ├── README.md
│   ├── WORKFLOW.md        # 開発ワークフロー全体
│   ├── SETUP_AND_MCP.md   # 環境構築・MCP設定
│   ├── NAMING_CONVENTIONS.md
│   ├── TESTING.md
│   ├── COMMIT_GUIDELINES.md
│   ├── PR_AND_REVIEW.md   # PR作成・レビュー・マージプロセス
│   └── ISSUE_GUIDELINES.md
├── docs/                  # プロジェクト固有情報
│   ├── requirements-definition.md  # 要件定義書
│   ├── ARCHITECTURE.md
│   ├── DATABASE.md
│   ├── API.md
│   ├── SETUP.md
│   ├── 2025-9-22.pdf      # 委託書サンプル
│   ├── テストシート.xlsx
│   ├── 請求書.xlsx
│   └── 資料作成注意点一覧.xlsx
├── frontend/              # Next.jsアプリ
│   ├── src/
│   │   ├── app/          # App Routerページ
│   │   ├── components/
│   │   ├── lib/
│   │   ├── hooks/
│   │   └── types/
│   └── package.json
├── backend/               # FastAPIアプリ
│   ├── app/
│   │   ├── models/       # SQLAlchemyモデル
│   │   ├── schemas/      # Pydanticスキーマ
│   │   ├── api/          # APIエンドポイント
│   │   └── core/
│   ├── migrations/        # Supabaseマイグレーション
│   └── requirements.txt
└── docker-compose.yml
```

## テストユーザー

```
Email: qa+shared@example.com
Password: SharedDev!2345
Username: qa_shared
User ID: 00000000-0000-4000-8000-000000000000

E2Eテスト用:
Email: test_e2e@example.com
Password: TestPass123!
```

## 主要ドキュメント

### 開発ルール
- [ai-rules/WORKFLOW.md](../ai-rules/WORKFLOW.md) - 全体ワークフロー
- [ai-rules/PR_AND_REVIEW.md](../ai-rules/PR_AND_REVIEW.md) - PR・レビュープロセス
- [ai-rules/NAMING_CONVENTIONS.md](../ai-rules/NAMING_CONVENTIONS.md) - 命名規則

### プロジェクト仕様
- [docs/requirements-definition.md](../docs/requirements-definition.md) - 要件定義書
- [docs/DATABASE.md](../docs/DATABASE.md) - データベース設計
- [docs/API.md](../docs/API.md) - API仕様

## 注意事項

- ✅ **毎セッション開始時にSerenaメモリから状況を把握する**
- ✅ **mainブランチへの直接作業は絶対禁止**
- ✅ **コミット前に必ず動作確認とE2Eテストを実施**
- ✅ **PR作成直後に必ずcode-reviewer サブエージェント レビューを依頼**
- ✅ **マージ後は必ず docs/ の更新が必要か確認する**
