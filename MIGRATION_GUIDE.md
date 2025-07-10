# Firebase Realtime Database から Firestore への移行ガイド

このガイドでは、既存の Web 勤怠システムを Firebase Realtime Database から Firestore Database に移行する手順を説明します。

## 移行の利点

### パフォーマンス向上

- **クエリ性能**: 複雑なクエリがより高速に実行
- **スケーラビリティ**: より多くのユーザーとデータに対応
- **インデックス**: 自動的なクエリ最適化

### データ構造の改善

- **ユーザー分離**: 各ユーザーのデータが独立したドキュメントに
- **階層構造**: より論理的なデータ組織
- **型安全性**: スキーマレスながらより構造化されたデータ

### 運用性の向上

- **バックアップ**: より柔軟なバックアップオプション
- **監視**: 詳細なメトリクスとログ
- **セキュリティ**: きめ細かい権限制御

## 移行前の準備

### 1. データのバックアップ

```bash
# 現在のデータをローカルにバックアップ
python -c "
from firebase_config import firebase_db
import json
data = firebase_db.load_data()
with open('backup_before_migration.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print('バックアップ完了: backup_before_migration.json')
"
```

### 2. Firestore プロジェクトの設定

詳細は [FIRESTORE_SETUP.md](./FIRESTORE_SETUP.md) を参照してください。

### 3. 必要な環境変数の設定

```bash
# .env ファイルまたは環境変数
export USE_FIRESTORE=true
export FIREBASE_PROJECT_ID=your-project-id
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
```

## 移行手順

### Step 1: Firestore コンポーネントのテスト

```bash
# Firestore統合テストを実行
python test_firestore.py
```

期待される出力:

```
=== テスト結果: 5/5 成功 ===
🎉 すべてのテストが成功しました！
```

### Step 2: データ移行の実行

#### 方法 A: 自動移行（推奨）

```bash
# Firestore版のアプリケーションを起動
python app_firestore.py
```

管理者アカウントでログイン後：

```bash
# 移行エンドポイントを呼び出し
curl -X POST http://localhost:5001/admin/migrate_to_firestore \
  -H "Content-Type: application/json" \
  -b "session=your-session-cookie"
```

#### 方法 B: 手動移行

```python
# manual_migration.py
from firebase_config import firebase_db
from attendance_firestore import firestore_attendance_manager
import json

# 従来データを読み込み
legacy_data = firebase_db.load_data()
print(f"従来データ読み込み: {len(legacy_data)}件")

# Firestoreに移行
success = firestore_attendance_manager.migrate_from_legacy_format(legacy_data)
if success:
    print("✓ 移行完了")
else:
    print("✗ 移行失敗")
```

### Step 3: データ整合性の確認

```python
# verify_migration.py
from firebase_config import firebase_db
from attendance_firestore import firestore_attendance_manager

# 従来データとFirestoreデータを比較
legacy_data = firebase_db.load_data()
firestore_data = firestore_attendance_manager.get_all_users_data()

print(f"従来データユーザー数: {len(legacy_data.get('users', {}))}")
print(f"Firestoreユーザー数: {len(firestore_data)}")

# 各ユーザーのデータ件数を確認
for username in legacy_data.get('users', {}):
    legacy_count = len(legacy_data['users'][username])
    firestore_count = len(firestore_data.get(username, {}))
    print(f"{username}: 従来={legacy_count}件, Firestore={firestore_count}件")
```

### Step 4: アプリケーションの切り替え

#### 段階的移行（推奨）

1. **テスト期間**: 両方のシステムを並行運用

```bash
# app.py（従来版）を port 5001 で起動
python app.py &

# app_firestore.py を port 5002 で起動
python app_firestore.py --port 5002 &
```

2. **検証期間**: 新しいデータを Firestore で記録

```bash
export USE_FIRESTORE=true
python app_firestore.py
```

3. **完全移行**: 従来版を停止

#### 一括移行

```bash
# 従来版をバックアップ
cp app.py app_legacy_backup.py

# Firestore版をメインに
cp app_firestore.py app.py

# 起動
export USE_FIRESTORE=true
python app.py
```

## 移行後の確認事項

### 1. 機能テスト

- [ ] ユーザー登録・ログイン
- [ ] 勤怠打刻
- [ ] 勤怠データ入力・編集
- [ ] Excel 出力
- [ ] 月別データ表示

### 2. パフォーマンステスト

```bash
# レスポンス時間の測定
curl -w "@curl-format.txt" -o /dev/null -s http://localhost:5001/attendance_info
```

### 3. データ整合性テスト

```python
# consistency_check.py
from auth_firestore import firestore_auth_manager
from attendance_firestore import firestore_attendance_manager

# 全ユーザーの勤怠データを確認
users = firestore_auth_manager.get_user_list()
for user in users:
    data = firestore_attendance_manager.get_user_attendance_data(user)
    print(f"{user}: {len(data)}日分のデータ")
```

## ロールバック手順

移行に問題がある場合の復旧方法：

### 1. 即座のロールバック

```bash
# Firestore版を停止
pkill -f app_firestore.py

# 従来版を起動
export USE_FIRESTORE=false
python app.py
```

### 2. データの復旧

```python
# restore_from_backup.py
import json
from firebase_config import firebase_db

# バックアップから復旧
with open('backup_before_migration.json', 'r', encoding='utf-8') as f:
    backup_data = json.load(f)

firebase_db.save_data(backup_data)
print("データ復旧完了")
```

## トラブルシューティング

### データ移行に失敗する場合

```bash
# ログを確認
tail -f firestore_migration.log

# 段階的移行を試行
python -c "
from attendance_firestore import firestore_attendance_manager
# 少量ずつ移行
"
```

### 認証エラーが発生する場合

```bash
# 認証情報を確認
echo $GOOGLE_APPLICATION_CREDENTIALS
echo $FIREBASE_SERVICE_ACCOUNT_JSON | jq .project_id
```

### パフォーマンスが低下する場合

1. Firestore インデックスを確認
2. クエリを最適化
3. キャッシュ設定を調整

## 移行後の最適化

### 1. インデックスの作成

Firebase Console で以下のインデックスを作成：

```
Collection: user_attendance
Fields: username (ASC), last_updated (DESC)
```

### 2. セキュリティルールの調整

```javascript
// より厳密なルール
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /user_attendance/{userId} {
      allow read, write: if request.auth.uid == userId;
    }
  }
}
```

### 3. バックアップスケジュールの設定

```bash
# 毎日のバックアップスクリプト
#!/bin/bash
DATE=$(date +%Y%m%d)
python -c "
from attendance_firestore import firestore_attendance_manager
firestore_attendance_manager.backup_to_json('daily_backup_${DATE}.json')
"
```

## サポート

移行に関する問題や質問がある場合：

1. ログファイルを確認
2. [FIRESTORE_SETUP.md](./FIRESTORE_SETUP.md) を参照
3. テストスクリプトを実行: `python test_firestore.py`
4. 必要に応じて Issue を作成

---

**注意**: 移行は本番環境で行う前に、必ずテスト環境で十分に検証してください。
