# Firebase 設定手順

## 1. Firebase プロジェクト作成

1. [Firebase Console](https://console.firebase.google.com/) にアクセス
2. 「プロジェクトを追加」をクリック
3. プロジェクト名を入力（例：`highflat-attendance`）
4. Google Analytics は無効で OK
5. 「プロジェクトを作成」をクリック

## 2. Realtime Database 設定

1. 左メニューから「Realtime Database」を選択
2. 「データベースを作成」をクリック
3. **場所**: `asia-southeast1` (シンガポール)を選択
4. **セキュリティルール**: 「テストモードで開始」を選択
5. 「有効にする」をクリック

## 3. データベース URL 取得

作成後、データベース URL が表示されます：

```
https://highflat-attendance-xxxxx-default-rtdb.asia-southeast1.firebasedatabase.app/
```

## 4. セキュリティルール設定（オプション）

セキュリティを強化したい場合、以下のルールを設定：

```json
{
  "rules": {
    "attendance_data": {
      ".read": true,
      ".write": true
    }
  }
}
```

## 5. Vercel 環境変数設定

1. Vercel ダッシュボード → プロジェクト → Settings → Environment Variables
2. 以下の環境変数を追加：

```
FIREBASE_URL = https://your-project-xxxxx-default-rtdb.asia-southeast1.firebasedatabase.app/
```

## 6. 再デプロイ

環境変数設定後、Vercel で再デプロイを実行してください。

## トラブルシューティング

### データベースアクセスエラー

- セキュリティルールで読み書きが許可されているか確認
- データベース URL が正しいか確認（末尾の `/` を含む）

### 環境変数が反映されない

- Vercel で環境変数設定後、再デプロイが必要
- `/debug_env` エンドポイントで環境変数を確認

## 無料プランでの制限

Firebase Realtime Database の無料プランの制限：

- **容量**: 1GB
- **同時接続**: 100 人
- **転送量**: 10GB/月

勤怠システムであれば十分な容量です。
