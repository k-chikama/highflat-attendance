# Firestore Database セットアップ手順

このドキュメントでは、Web 勤怠システムで Firestore Database を構築・設定する手順を説明します。

## 概要

このシステムでは以下の 3 つのデータベースオプションを提供しています：

1. **Firestore Database** （推奨） - スケーラブルで高性能な NoSQL データベース
2. **Firebase Realtime Database** - 従来版との互換性のため
3. **ローカルファイルストレージ** - 開発環境での使用

## Firestore Database の利点

- **高性能**: より高速なクエリとスケーラビリティ
- **構造化データ**: ドキュメント＋コレクション形式でデータを整理
- **強整合性**: より信頼性の高いデータ整合性
- **より良いセキュリティルール**: 細かい権限制御が可能
- **オフライン対応**: クライアント側でのオフライン機能
- **リアルタイム更新**: データ変更の即座の反映

## セットアップ手順

### 1. Firebase プロジェクトの作成

1. [Firebase Console](https://console.firebase.google.com/) にアクセス
2. 「プロジェクトを追加」をクリック
3. プロジェクト名を入力（例: `highflat-attendance`）
4. 必要に応じて Google Analytics を有効化
5. 「プロジェクトを作成」をクリック

### 2. Firestore Database の有効化

1. Firebase Console でプロジェクトを選択
2. 左サイドバーの「Firestore Database」をクリック
3. 「データベースの作成」をクリック
4. セキュリティルールを選択：
   - **本番環境**: 「本番モードで開始」を選択
   - **テスト環境**: 「テストモードで開始」を選択（60 日間）
5. ロケーションを選択（推奨: `asia-northeast1 (Tokyo)`）
6. 「完了」をクリック

### 3. サービスアカウントキーの作成

1. Firebase Console で「プロジェクトの設定」（歯車アイコン）をクリック
2. 「サービスアカウント」タブを選択
3. 「新しい秘密鍵の生成」をクリック
4. 生成された JSON ファイルをダウンロード
5. **重要**: このファイルは機密情報です。安全な場所に保管してください

### 4. セキュリティルールの設定

Firestore Console で「ルール」タブを選択し、以下のルールを設定：

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // ユーザー認証済みのみアクセス可能
    match /{document=**} {
      allow read, write: if request.auth != null;
    }

    // ユーザーコレクション（ユーザー名ベースのアクセス制御）
    match /users/{userId} {
      allow read, write: if request.auth != null &&
                           request.auth.token.email == userId + "@yourcompany.com";
    }

    // 勤怠データ（ユーザー自身のデータのみアクセス可能）
    match /user_attendance/{userId} {
      allow read, write: if request.auth != null &&
                           resource.data.username == request.auth.token.email.split('@')[0];
    }
  }
}
```

## 環境変数の設定

### ローカル開発環境

プロジェクトルートに `.env` ファイルを作成（または環境変数を設定）：

```bash
# Firestore設定
USE_FIRESTORE=true
FIREBASE_PROJECT_ID=your-project-id
GOOGLE_APPLICATION_CREDENTIALS=path/to/your/service-account-key.json

# または、JSONファイルの内容を直接環境変数に設定
FIREBASE_SERVICE_ACCOUNT_JSON='{"type":"service_account","project_id":"your-project-id",...}'

# セキュリティ
SECRET_KEY=your-super-secret-key-for-flask-sessions
```

### Vercel 本番環境

Vercel Dashboard の Environment Variables で以下を設定：

```bash
USE_FIRESTORE=true
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_SERVICE_ACCOUNT_JSON={"type":"service_account","project_id":"your-project-id",...}
SECRET_KEY=your-super-secret-key-for-flask-sessions
```

**注意**: `FIREBASE_SERVICE_ACCOUNT_JSON` は、サービスアカウントキーの JSON ファイル全体を文字列として設定してください。

## データ構造

Firestore では以下のコレクション構造を使用します：

```
/users/{username}
  - username: string
  - password_hash: string
  - display_name: string
  - created_at: timestamp

/user_attendance/{username}
  - username: string
  - attendance_data: map
    - "2025-07-10": map
      - check_in: "09:00"
      - check_out: "18:00"
      - break_time: "60"
      - transport_fee: "500"
      - station_name: "東京駅"
      - notes: "定時"
  - last_updated: timestamp

/user_sessions/{session_id}
  - username: string
  - session_id: string
  - created_at: timestamp
```

## 使用方法

### Firestore モードで起動

```bash
# 環境変数を設定
export USE_FIRESTORE=true
export FIREBASE_PROJECT_ID=your-project-id
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json

# アプリケーション起動
python app_firestore.py
```

### 従来モードからの移行

1. 管理者権限でログイン
2. `/admin/migrate_to_firestore` エンドポイントに POST リクエストを送信
3. 従来のデータが Firestore に移行されます

```bash
curl -X POST http://localhost:5001/admin/migrate_to_firestore \
  -H "Content-Type: application/json" \
  -b "your-session-cookie"
```

## トラブルシューティング

### 認証エラー

```
ERROR: Firebase認証情報が見つかりません
```

**解決方法**:

- `GOOGLE_APPLICATION_CREDENTIALS` 環境変数が正しいパスを指しているか確認
- または `FIREBASE_SERVICE_ACCOUNT_JSON` に正しい JSON が設定されているか確認

### 権限エラー

```
ERROR: permission denied
```

**解決方法**:

- Firestore セキュリティルールを確認
- サービスアカウントに適切な権限があるか確認

### 接続エラー

```
ERROR: connection failed
```

**解決方法**:

- `FIREBASE_PROJECT_ID` が正しいか確認
- ネットワーク接続を確認
- Firebase プロジェクトが有効になっているか確認

## パフォーマンス最適化

### インデックスの作成

よく使用するクエリに対して Firestore Console でインデックスを作成：

1. Firestore Console の「インデックス」タブを選択
2. 以下のインデックスを作成：
   - Collection: `user_attendance`, Fields: `username` (ASC), `last_updated` (DESC)

### キャッシュの活用

アプリケーションでは以下のキャッシュ戦略を使用：

- **メモリキャッシュ**: よくアクセスされるユーザーデータ
- **ローカルファイルバックアップ**: ネットワーク障害時のフォールバック

## バックアップとリストア

### 手動バックアップ

```python
from attendance_firestore import firestore_attendance_manager

# データをJSONファイルにバックアップ
firestore_attendance_manager.backup_to_json('backup_2025_07_10.json')
```

### 復元

```python
from attendance_firestore import firestore_attendance_manager

# JSONファイルからデータを復元
firestore_attendance_manager.restore_from_json('backup_2025_07_10.json')
```

### 自動バックアップ

Firestore の自動バックアップを設定：

1. Google Cloud Console で「Cloud Firestore」を選択
2. 「バックアップ」タブを選択
3. 「スケジュールの作成」をクリック
4. バックアップの頻度とリテンション期間を設定

## セキュリティベストプラクティス

1. **最小権限の原則**: 必要最小限の権限のみを付与
2. **環境変数の管理**: 機密情報は環境変数で管理
3. **定期的な監査**: Firestore セキュリティルールの定期見直し
4. **ログ監視**: 異常なアクセスパターンの監視

## サポート

問題が発生した場合：

1. ログを確認（`DEBUG:`で始まる行）
2. 環境変数の設定を再確認
3. Firebase Console でプロジェクトの状態を確認
4. 必要に応じて Issue を作成
