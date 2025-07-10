# Vercel + Firestore デプロイガイド

## 🚀 概要

Firestore ベースの勤怠システムを Vercel にデプロイするための完全ガイドです。

## 🔧 前提条件

- GitHub アカウント
- Vercel アカウント
- Firebase プロジェクト (Firestore 有効化済み)
- Firebase Service Account キー

## 📋 デプロイ手順

### 1. Firebase Service Account キーの準備

Firebase Console から Service Account キーファイルを取得し、Base64 エンコードします：

```bash
# Service Account キーをBase64エンコード
cat firebase-service-account.json | base64 | tr -d '\n'
```

### 2. Vercel プロジェクトの作成

1. Vercel にログイン
2. "New Project" をクリック
3. GitHub リポジトリを選択 (`highflat-attendance`)
4. 環境変数を設定（下記参照）

### 3. 環境変数の設定

Vercel ダッシュボードで以下の環境変数を設定：

#### 🔥 Firestore 設定（必須）

```
USE_FIRESTORE=true
FIREBASE_PROJECT_ID=your-project-id
GOOGLE_APPLICATION_CREDENTIALS_BASE64=<base64エンコードされたサービスアカウントキー>
```

#### 🔄 従来版フォールバック（オプション）

```
GIST_ID=your_gist_id_here
GITHUB_TOKEN=your_github_token_here
```

### 4. デプロイ実行

1. "Deploy" をクリック
2. デプロイ完了後、提供された URL でアクセス

## 🏗️ システム構成

### アプリケーション選択

WSGI エントリーポイント (`wsgi.py`) が自動的に適切なアプリケーションを選択：

- `USE_FIRESTORE=true` → `app_firestore.py` (Firestore ベース)
- `USE_FIRESTORE=false` → `app.py` (従来版)

### データストレージ

- **Firestore**: スケーラブル、リアルタイム同期
- **GitHub Gist**: 従来版フォールバック

## ⚙️ 設定例

### 本番環境 (推奨)

```
USE_FIRESTORE=true
FIREBASE_PROJECT_ID=highflat-attendance
GOOGLE_APPLICATION_CREDENTIALS_BASE64=ewogICJ0eXBlIjogInNlcnZpY2VfYWNjb3VudCIsC...
```

### 開発/テスト環境

```
USE_FIRESTORE=false
GIST_ID=1234567890abcdef
GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxxx
```

## 🔒 セキュリティ

### Service Account キー管理

1. **Base64 エンコード**: セキュアな環境変数保存
2. **最小権限**: Firestore 読み書きのみ
3. **ローテーション**: 定期的なキー更新

### 認証システム

- パスワードハッシュ化 (bcrypt)
- セッション管理 (Firestore)
- セキュア Cookies

## 📊 機能

### ✅ 利用可能機能

- ユーザー認証・登録
- 勤怠打刻・管理
- Excel レポート出力
- リアルタイムデータ同期
- 自動バックアップ

### 📈 Firestore 利点

- **スケーラビリティ**: 大量データ対応
- **リアルタイム**: 即座に反映
- **信頼性**: 99.999% 可用性
- **セキュリティ**: Firebase Security Rules

## 🐛 トラブルシューティング

### Firestore 接続エラー

```
ERROR: Firebase認証情報が見つかりません
```

**解決策:**

1. `GOOGLE_APPLICATION_CREDENTIALS_BASE64` の設定確認
2. Base64 エンコードの正確性確認
3. Firestore API 有効化確認

### デプロイエラー

```
ERROR: Module 'google-cloud-firestore' not found
```

**解決策:**

1. `requirements.txt` に依存関係追加済みか確認
2. Vercel ビルドログ確認

### 認証問題

```
ERROR: ユーザー登録に失敗
```

**解決策:**

1. Firestore Security Rules 確認
2. Service Account 権限確認

## 📝 ログとモニタリング

### Vercel ログ確認

```bash
vercel logs [deployment-url]
```

### Firebase Console 確認

1. [Firebase Console](https://console.firebase.google.com/) アクセス
2. プロジェクト選択
3. Firestore Database → データ確認

## 🔄 継続的デプロイ

### 自動デプロイ設定

1. GitHub リポジトリ連携済み
2. `main` ブランチへのプッシュで自動デプロイ
3. プルリクエストでプレビューデプロイ

### デプロイ確認手順

1. ✅ ビルド成功
2. ✅ 環境変数設定
3. ✅ Firestore 接続
4. ✅ 認証機能
5. ✅ Excel 出力

## 📞 サポート

### デプロイ支援

- Firestore 設定支援
- 環境変数設定支援
- トラブルシューティング

### 技術仕様

- **Runtime**: Python 3.9
- **Framework**: Flask 2.3.7
- **Database**: Google Cloud Firestore
- **Hosting**: Vercel
- **Authentication**: Custom + Firestore
