# Vercel 環境変数設定ガイド

## 📋 必要な環境変数

### 1. USE_FIRESTORE

- **Value**: `true`
- **説明**: Firestore を使用するフラグ

### 2. FIREBASE_PROJECT_ID

- **Value**: `highflat-attendance`
- **説明**: Firebase プロジェクトの ID

### 3. GOOGLE_APPLICATION_CREDENTIALS_BASE64

- **Value**: Firebase Service Account Key の Base64 エンコード文字列
- **説明**: Firestore 認証用のクレデンシャル

## 🔧 設定手順

### Step 1: Firebase Service Account Key の Base64 エンコード

**macOS の場合:**

```bash
cat firebase-service-account.json | base64 | tr -d '\n'
```

**Windows の場合:**

```powershell
[Convert]::ToBase64String([IO.File]::ReadAllBytes("firebase-service-account.json"))
```

### Step 2: Vercel Dashboard での設定

1. Vercel プロジェクト画面で **"Settings"** タブをクリック
2. 左サイドバーの **"Environment Variables"** をクリック
3. 以下の順序で環境変数を追加:

#### 環境変数 1: USE_FIRESTORE

- **Name**: `USE_FIRESTORE`
- **Value**: `true`
- **Environments**: Production, Preview, Development すべてチェック
- "Save" をクリック

#### 環境変数 2: FIREBASE_PROJECT_ID

- **Name**: `FIREBASE_PROJECT_ID`
- **Value**: `highflat-attendance`
- **Environments**: Production, Preview, Development すべてチェック
- "Save" をクリック

#### 環境変数 3: GOOGLE_APPLICATION_CREDENTIALS_BASE64

- **Name**: `GOOGLE_APPLICATION_CREDENTIALS_BASE64`
- **Value**: [Base64 エンコードした文字列を貼り付け]
- **Environments**: Production, Preview, Development すべてチェック
- "Save" をクリック

⚠️ **注意**: Base64 文字列は約 2000 文字と長いので、コピペ時に途切れないよう注意

## ✅ 設定確認

環境変数が正しく設定されると、Environment Variables 画面に以下が表示されます:

```
USE_FIRESTORE                           Production, Preview, Development
FIREBASE_PROJECT_ID                     Production, Preview, Development
GOOGLE_APPLICATION_CREDENTIALS_BASE64   Production, Preview, Development
```

## 🚨 トラブルシューティング

### Base64 エンコードエラー

- 改行文字が混入している可能性
- 以下のコマンドで確実に除去:

```bash
cat firebase-service-account.json | base64 | tr -d '\n\r' | pbcopy
```

### JSON 形式エラー

- firebase-service-account.json が有効な JSON かチェック:

```bash
python -m json.tool firebase-service-account.json
```

### 文字数制限

- Vercel の環境変数は 64KB 制限
- Firebase Service Account Key は通常 2KB 程度なので問題なし
