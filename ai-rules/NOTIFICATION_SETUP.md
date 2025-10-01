# Discord Webhook通知設定

## 概要

PRコメント（Codexレビュー含む）やPR作成・更新イベントをDiscordへ自動通知する設定です。

## 通知されるイベント

- ✅ **Issue comments** - PRへのコメント（Codexレビュー含む）
- ✅ **Pull requests** - PR作成・クローズ・マージ
- ✅ **Pull request reviews** - レビュー完了
- ✅ **Pull request review comments** - レビューコメント

## 初回設定手順

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

### ステップ3: 動作確認

1. テストPRを作成

2. PRにコメントを投稿
   ```
   テスト通知
   ```

3. Discordチャンネルに通知が届くことを確認

## 通知の見え方

### PR作成時
```
[owner/repo] Pull request opened: #123 タイトル
概要と変更内容
```

### PRコメント時
```
[owner/repo] New comment on pull request #123: タイトル
コメント内容
```

### Codexレビュー時
```
[owner/repo] New comment on pull request #123: タイトル
@codex: レビューコメント内容
```

## トラブルシューティング

### 通知が届かない場合

1. **Webhook URLを確認**
   - 末尾に `/github` が付いているか
   - URLに誤字がないか

2. **イベント設定を確認**
   - 必要なイベントにチェックが入っているか
   - Activeがオンになっているか

3. **GitHub Webhookのログを確認**
   - Settings → Webhooks → 該当Webhook
   - 「Recent Deliveries」タブでエラーを確認

4. **Discordの権限を確認**
   - Webhookを作成したチャンネルへの投稿権限があるか

### 通知が重複する場合

- Webhookが複数登録されていないか確認
- 不要なWebhookは削除

## セキュリティ注意事項

- Webhook URLを公開しない
- リポジトリのSecrets機能は使用不可（GitHub Webhook設定のため）
- 不要になったWebhookは削除する
- 定期的にWebhookの設定を見直す

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
