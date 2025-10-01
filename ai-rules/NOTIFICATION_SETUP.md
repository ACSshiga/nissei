# Discord通知設定

## 概要

GitHub上のPRイベント（コメント、レビュー等）をDiscordへ自動通知する設定です。

## 通知方法

### GitHub Webhook（推奨）

GitHub Webhookを使用して、PRイベントをDiscordに通知します。

**特徴**:
- ✅ シンプルな設定
- ✅ リアルタイム通知
- ✅ GitHub標準機能

## 通知されるイベント

- ✅ **Issue comments** - PRへのコメント
- ✅ **Pull requests** - PR作成・更新・マージ
- ✅ **Pull request reviews** - レビュー完了
- ✅ **Pull request review comments** - レビューコメント

## GitHub Webhook設定手順

### ステップ1: Discord Webhook URL取得

1. Discordサーバーで通知用チャンネルを作成
   - 推奨チャンネル名: `#github-notifications`

2. チャンネル設定を開く
   - チャンネル名を右クリック → 「チャンネルの編集」

3. 連携サービス → Webhook
   - 「Webhookを作成」をクリック

4. Webhook URLをコピー
   - 形式: `https://discord.com/api/webhooks/{id}/{token}`
   - **重要**: このURLを安全に保管

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

## 通知の見え方

Discordに以下のような埋め込みメッセージが表示されます：

```
[ShigaRyunosuke10/nissei] Pull request opened by username
#17: ドキュメント構造を再編成

[View pull request]（リンク）
```

## トラブルシューティング

### 通知が届かない場合

1. **Webhook URLを確認**
   - 末尾に `/github` が付いているか
   - URLに誤字がないか

2. **GitHub Webhookのログを確認**
   - Settings → Webhooks → 該当Webhook
   - 「Recent Deliveries」タブでエラーを確認

3. **Discordの権限を確認**
   - Webhookを作成したチャンネルへの投稿権限があるか

## セキュリティ注意事項

- **Discord Webhook URLを公開しない**
  - 安全に保管
  - コードやコミットメッセージに含めない

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
