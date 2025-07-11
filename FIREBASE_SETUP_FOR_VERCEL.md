# Firebase Service Account Key 設定ガイド（Vercel 用）

## 🔐 Firebase Service Account Key の取得

### 1. Firebase Console にアクセス

1. [Firebase Console](https://console.firebase.google.com/) にアクセス
2. `highflat-attendance` プロジェクトを選択

### 2. Service Account Key の生成

1. 左サイドバーの歯車アイコン → "Project settings" をクリック
2. "Service accounts" タブを選択
3. "Generate new private key" ボタンをクリック
4. JSON 形式でキーファイルがダウンロードされます
5. ファイル名を `firebase-service-account.json` に変更

### 3. Base64 エンコード

ダウンロードしたキーファイルを Base64 エンコードします：

**macOS/Linux:**

```bash
cat firebase-service-account.json | base64 | tr -d '\n'
```

**Windows (PowerShell):**

```powershell
[Convert]::ToBase64String([IO.File]::ReadAllBytes("firebase-service-account.json"))
```

### 4. 出力例

Base64 エンコード後、以下のような長い文字列が出力されます：

```
ewogICJ0eXBlIjogInNlcnZpY2VfYWNjb3VudCIsC...（約2000文字）
```

この文字列全体をコピーして、Vercel の環境変数 `GOOGLE_APPLICATION_CREDENTIALS_BASE64` に設定してください。

## ⚠️ セキュリティ注意事項

1. **Service Account Key は機密情報です**

   - GitHub 等にコミットしないでください
   - チームメンバーとの共有は必要最小限に

2. **権限設定**

   - Firebase Console → IAM で Service Account の権限を確認
   - Firestore の読み書き権限のみで十分です

3. **定期的なローテーション**
   - セキュリティ向上のため、定期的にキーを再生成することを推奨

## 🔍 トラブルシューティング

### Base64 エンコードエラー

```bash
# 改行文字を確実に除去
cat firebase-service-account.json | base64 | tr -d '\n' | pbcopy
```

### キーファイルが見つからない

Firebase Console → Project Settings → Service Accounts で再度ダウンロード

### 権限エラー

Firebase Console → IAM で Service Account に `Cloud Datastore User` ロールを付与
