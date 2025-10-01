# Discord通知設定

## 概要

**Codexレビューのみ**をDiscordへ自動通知する設定です。

## 通知方法

### 推奨: GitHub Actions（Codexレビューのみ通知）

GitHub Actionsを使用して、Codexからのレビュー・コメントのみをDiscordに通知します。

**メリット**:
- ✅ Codexのコメント・レビューのみを通知
- ✅ 他のPRコメントは通知されない
- ✅ きめ細かい制御が可能

### 非推奨: GitHub Webhook（全イベント通知）

GitHub Webhookを直接使用すると、すべてのPRイベントが通知されます。

**デメリット**:
- ❌ すべてのPRコメントが通知される
- ❌ 特定ユーザーでフィルタリング不可
- ❌ 通知が多すぎる可能性

## 通知されるイベント（GitHub Actions使用時）

- ✅ **Codexからのissue comments** - Codexの`@codex review`コメント
- ✅ **Codexからのpull request reviews** - Codexのレビュー完了
- ✅ **Codexからのpull request review comments** - Codexのレビューコメント

⚠️ **重要**: 他のユーザーからのコメント・レビューは通知されません

## GitHub Actions設定手順（推奨）

### ステップ1: Discord Webhook URL取得

1. Discordサーバーで通知用チャンネルを作成
   - 推奨チャンネル名: `#codex-reviews`

2. チャンネル設定を開く
   - チャンネル名を右クリック → 「チャンネルの編集」

3. 連携サービス → Webhook
   - 「Webhookを作成」をクリック

4. Webhook URLをコピー
   - 形式: `https://discord.com/api/webhooks/{id}/{token}`
   - **重要**: このURLを安全に保管（末尾の`/github`は不要）

### ステップ2: GitHub Secretsに登録

1. GitHubリポジトリのSettings → Secrets and variables → Actionsにアクセス
   - URL: `https://github.com/{owner}/{repo}/settings/secrets/actions`

2. 「New repository secret」をクリック

3. 以下を入力:
   - **Name**: `DISCORD_WEBHOOK_URL`
   - **Secret**: コピーしたDiscord Webhook URL
   - 「Add secret」をクリック

### ステップ3: GitHub Actionsワークフローを配置

リポジトリに以下のファイルが既に存在します：
```
.github/workflows/codex-review-notification.yml
```

このファイルが、Codexからのレビュー・コメントのみをDiscordに通知します。

### ステップ4: 動作確認

1. PRにCodexレビューを依頼
   ```
   @codex review
   ```

2. Codexがレビューを投稿

3. Discordの`#codex-reviews`チャンネルに通知が届くことを確認

4. **確認項目**:
   - ✅ Codexのコメントのみが通知される
   - ❌ 他のユーザーのコメントは通知されない

## GitHub Webhook設定（非推奨）

⚠️ この方法ではすべてのPRイベントが通知されます。Codexのみに限定したい場合は、上記のGitHub Actions設定を使用してください。

<details>
<summary>GitHub Webhook設定手順（クリックして展開）</summary>

### ステップ1: Discord Webhook URL取得

上記と同じ手順でDiscord Webhook URLを取得します。

### ステップ2: GitHub Webhook設定

1. GitHubリポジトリのSettings → Webhooksにアクセス
   - URL: `https://github.com/{owner}/{repo}/settings/hooks`

2. 「Add webhook」をクリック

3. 以下の項目を入力:

   **Payload URL**
   ```
   https://discord.com/api/webhooks/{id}/{token}/github
   ```
   ⚠️ **重要**: 末尾に `/github` を必ず追加

   **Content type**
   ```
   application/json
   ```

   **Which events would you like to trigger this webhook?**
   - 「Let me select individual events」を選択
   - 以下の4つにチェック:
     - ✅ Issue comments
     - ✅ Pull requests
     - ✅ Pull request reviews
     - ✅ Pull request review comments

   **Active**
   - ✅ チェックを入れる

4. 「Add webhook」をクリック

**デメリット**: すべてのコメント・レビューが通知されるため、通知が多くなります。

</details>

## 通知の見え方（GitHub Actions使用時）

Discordに以下のような埋め込みメッセージが表示されます：

```
🤖 Codex Review on PR #16
ドキュメント構造を再編成

Event Type: issue_comment
Repository: ShigaRyunosuke10/nissei

Comment Preview:
**<sub><sub>![P1 Badge](https://img.shields.io/badge/P1-orange?style=flat)</sub></sub>  Quickstart copies a non-existent .env.example**

The new quickstart instructs `cp .env.example .env`, but the repository only ships environment exam...

[コメントを見る]（リンク）
```

## トラブルシューティング

### 通知が届かない場合（GitHub Actions）

1. **GitHub Secretを確認**
   - `DISCORD_WEBHOOK_URL` が正しく設定されているか
   - Settings → Secrets and variables → Actions で確認

2. **GitHub Actionsのログを確認**
   - Actions タブで最新のワークフロー実行を確認
   - エラーメッセージがあれば内容を確認

3. **Discord Webhook URLを確認**
   - URLに誤字がないか
   - 末尾に`/github`は**付けない**（GitHub Actions用）

4. **Discordの権限を確認**
   - Webhookを作成したチャンネルへの投稿権限があるか

### 通知が届かない場合（GitHub Webhook - 非推奨）

1. **Webhook URLを確認**
   - 末尾に `/github` が付いているか
   - URLに誤字がないか

2. **GitHub Webhookのログを確認**
   - Settings → Webhooks → 該当Webhook
   - 「Recent Deliveries」タブでエラーを確認

### すべてのコメントが通知される場合

GitHub Webhookを使用している可能性があります：

1. **GitHub Webhookを無効化または削除**
   - Settings → Webhooks
   - 該当Webhookを削除または「Active」のチェックを外す

2. **GitHub Actionsに切り替え**
   - 上記の「GitHub Actions設定手順」を実施

## セキュリティ注意事項

- **Discord Webhook URLを公開しない**
  - GitHub Secretsに安全に保管
  - コードやコミットメッセージに含めない

- **GitHub Secretsを使用**（GitHub Actions使用時）
  - `DISCORD_WEBHOOK_URL` をSecretsに登録
  - 環境変数として安全に使用

- **不要になったWebhookは削除**
  - Discordの古いWebhook
  - GitHubの古いWebhook設定

- **定期的に設定を見直す**
  - 使用していないWebhookは削除
  - アクセス権限を確認

## メンテナンス

### Webhook URL変更時

1. Discordで新しいWebhookを作成
2. GitHubのWebhook設定で Payload URLを更新
3. 古いWebhookを削除（Discord・GitHub両方）

### 通知チャンネル変更時

1. 新しいDiscordチャンネルでWebhookを作成
2. GitHubのWebhook設定を更新
3. 古い設定を削除

## 参考リンク

- [GitHub Webhooks Documentation](https://docs.github.com/webhooks)
- [Discord Webhooks Guide](https://discord.com/developers/docs/resources/webhook)
