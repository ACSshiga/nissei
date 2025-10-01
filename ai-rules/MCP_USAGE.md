MCP サーバー運用ガイド（追記用）

対象リポジトリ: CLAUDE.md に記載
開発ポート固定: Frontend 3000 / Backend 8000（変更禁止）
.env は UPPER_SNAKE_CASE・値はクォート無し。API キー類はコミットしない（.gitignore 必須）

共通：起動・接続の流れ（Claude Code から利用）

上記 JSON（mcpServers）をクライアント（Claude Code）の設定ファイルに反映

ローカルでクライアントを再起動 → セッション開始時に各 MCP が自動起動（type: "stdio"）または HTTP 接続

実行時は 目的別にサーバーを明示して指示（例：「playwright で E2E を走らせて」）

セキュリティ注意：設定 JSON 内のトークンは .env に退避し、env で参照＋.gitignore に追加。
例）GITHUB_TOKEN, CONTEXT7_API_KEY, SUPABASE_ACCESS_TOKEN など。

1. context7 （Upstash Context7 MCP）

用途（RAG/検索支援）

ローカル/URL/リポジトリのドキュメントを取り込み → 質問応答や類似検索。

設計検討前の “情報収集フェーズ” に有効。

起動

すでに設定済み: npx @upstash/context7-mcp --api-key <KEY>（CONTEXT7_API_KEY を .env に）

代表プロンプト

「context7 に docs/ と backend/ をインデックスして。終わったら ‘準備 OK’ と返して」

「次の記事 URL を取り込んで要点 5 つに要約して: <URL>」

「FastAPI のエラーハンドリング方針に関する社内文書の要点を列挙して」

注意

取り込み対象に秘密情報が含まれないか要確認

重要文書はパス/グロブで選別し、極力最小限に

2. playwright（公式 MCP）

用途（E2E 自動テスト）

必須確認事項に記載の通り、コミット前に E2E を実行。

テスト作成・実行・スクショ/動画保存・レポート確認。

起動

設定済み: npx @playwright/mcp@latest

代表プロンプト

「playwright で tests/e2e/login.spec.ts を実行、結果と失敗スクショを出力して」

「ユーザー xxx/xxx でログイン → ダッシュボードの ‘Welcome, xxx’ を検証する E2E を新規作成して」

「テスト前に http://localhost:3000
と http://localhost:8000
の起動待ちを入れて（タイムアウト 60 秒）」

注意

3000/8000 のポート固定（競合時は他プロセスを kill して既定ポートで実行）

CI でのヘッドレス実行も想定し、storageState 等を活用

3. github（HTTP / Copilot MCP 経由）

用途（Issue/PR 操作の自動化）

常にリポジトリ xxx を対象に Issue 作成、PR 作成、ラベル付与、レビュー依頼、コメント投稿など。

起動

設定済み URL へ HTTP 接続（Authorization: Bearer <GITHUB_TOKEN> は .env 管理）

代表プロンプト

「xxx に ISSUE_GUIDELINES.md の作成タスクを issue 登録。テンプレは ai-rules の規約に沿って。ラベルは documentation と priority: high」

「ブランチ feat-issue-guidelines の PR を main 向けに作成。本文に Closes #<issue 番号> と E2E 結果を記載して」

「この PR にレビューア @<member> を追加して、ラベル enhancement を付けて」

注意

トークン露出禁止（.env に退避）

プロジェクトが複数ある場合でも 対象は xxx に固定（誤操作防止）

4. desktop-commander

用途（ローカル PC の操作自動化）

画面操作/アプリ起動/キーボード入力/プロセス操作など。

手動での“環境準備”や“一発コマンド”を代行させたいとき。

代表プロンプト

「ターミナルを開いて lsof -i :8000 → 該当 PID があれば kill -9 <PID> を実行」

「Chrome を起動して http://localhost:3000 を全画面表示、ロード後にスクショを保存」

「VS Code を開いて ai-rules/ISSUE_GUIDELINES.md を新規作成、下書きを貼り付けて保存」

注意

誤操作リスクがあるため、操作範囲を明示（アプリ名/パス/許可ダイアログ対応）

機密画面のスクショ取得は禁止

5. serena

用途（高度な自動化・エージェント連携の土台）

uvx --from git+https://github.com/oraios/serena で配布される MCP。

一般にスクリプト実行・ファイル操作・ワークフロー実行といった複合タスクをハンドリングする用途が多い。

代表プロンプト

「backend/ の FastAPI ルータを走査してエンドポイント一覧の Markdown を出力して」

「schemas.py と routers/ の対応関係を可視化する表を作って」

「/health の E2E を自動生成し、playwright で実行 → レポート保存」

注意

実行系のツールが含まれる場合、変更前に差分プランの提示を必須化（破壊的変更対策）

---

## PRレビューで使用しなくなったツール

### codex（理由：時間がかかりすぎるため）

**変更内容**: PRレビューには Claude Code のサブエージェント機能（Task tool）を使用するように変更しました。

**理由**: Codex MCPはレビューに時間がかかりすぎるため、より高速なTask toolに切り替え。

**Task toolでの代替方法**:
- PRレビュー: Task toolでコードレビューを依頼（高速）
- 複雑なタスク: Task toolで段階的に調査・実装を依頼
- アーキテクチャ相談: 直接Claude Codeに相談

**注意**: Codex MCP自体は引き続き利用可能です。深掘り解析やアーキテクチャ相談など、時間をかけても詳細な分析が必要な場合は使用できます。

---

6. supabase

用途（DB/認証/ストレージ連携）

Supabase プロジェクト（--project-ref=wwyrthkizkcgndyorcww）に対するスキーマ確認・SQL 実行・ストレージ操作など。

代表プロンプト

「public スキーマのテーブル一覧とカラム情報を取得して Markdown で整形」

「users に plan 列（enum: free/pro）を追加するマイグレーション案を生成し、ロールバック SQL も併記」

「ストレージに playwright-report/ を作成して最新レポートをアップロード」

注意

本番データへの影響に注意（dry-run や 確認プロンプトを挟む）

秘密鍵/サービスロールキーは厳重管理（.env & .gitignore）
