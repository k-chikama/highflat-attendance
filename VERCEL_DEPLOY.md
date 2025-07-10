# Vercel デプロイガイド

## 概要

この Web 勤怠システムを Vercel にデプロイするための手順です。

## 前提条件

- GitHub アカウント
- Vercel アカウント
- GitHub Personal Access Token

## デプロイ手順

### 1. GitHub Personal Access Token の作成

1. GitHub にログイン
2. Settings > Developer settings > Personal access tokens > Tokens (classic)
3. "Generate new token" をクリック
4. 以下の権限を選択：
   - `gist` (Gist の作成・編集)
5. トークンを生成し、安全な場所に保存

### 2. GitHub Gist の作成

1. GitHub で新しい Gist を作成
2. ファイル名: `attendance_data.json`
3. 内容: `{}`
4. "Create secret gist" をクリック
5. Gist の URL から ID を取得（例: `https://gist.github.com/username/1234567890abcdef` → `1234567890abcdef`）

### 3. Vercel プロジェクトの作成

1. Vercel にログイン
2. "New Project" をクリック
3. GitHub リポジトリを選択
4. 以下の環境変数を設定：
   - `GIST_ID`: 作成した Gist の ID
   - `GITHUB_TOKEN`: 作成した Personal Access Token

### 4. デプロイ

1. "Deploy" をクリック
2. デプロイ完了後、提供された URL でアクセス

## 環境変数の設定

Vercel のダッシュボードで以下の環境変数を設定してください：

```
GIST_ID=your_gist_id_here
GITHUB_TOKEN=your_github_token_here
```

## 注意事項

### データ永続化

- Vercel はサーバーレス環境のため、ファイルシステムへの書き込みは永続化されません
- このシステムでは GitHub Gist を使用してデータを永続化しています
- 環境変数が設定されていない場合、ローカルファイルシステムを使用します

### セキュリティ

- GitHub Personal Access Token は機密情報です
- トークンは必要最小限の権限（gist）のみを付与してください
- トークンが漏洩した場合は、すぐに再生成してください

### 制限事項

- GitHub API の制限により、短時間での大量アクセスは制限される場合があります
- Gist のサイズ制限により、大量のデータは保存できません

## トラブルシューティング

### 打刻が反映されない

1. 環境変数が正しく設定されているか確認
2. GitHub Personal Access Token の権限を確認
3. Gist ID が正しいか確認
4. Vercel のログでエラーを確認

### jpholiday エラー

- Vercel は Python 3.9 を使用
- requirements.txt で jpholiday==1.0.2 を指定済み

### その他の問題

- Vercel のダッシュボードでログを確認
- GitHub API の制限に達していないか確認
