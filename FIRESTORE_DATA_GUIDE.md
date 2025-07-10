# Firestore データベース 表示・管理ガイド

## 📊 データベース概要

Firestore データベースには以下のデータが保存されています：

- **12 ユーザー分の勤怠データ** - 258 件の記録
- **統合勤怠データ** - 2025 年 7 月分（31 日間）
- **ユーザー jpz4149 の個人データ** - 最新の打刻記録

## 🔍 データ表示ツール

### 1. シンプル表示ツール `simple_firestore_viewer.py`

**基本使用方法:**

```bash
# 全データ表示
python simple_firestore_viewer.py

# サマリーのみ表示
python simple_firestore_viewer.py --summary

# 詳細データ表示
python simple_firestore_viewer.py --detailed

# データエクスポート
python simple_firestore_viewer.py --export [ファイル名]

# ヘルプ表示
python simple_firestore_viewer.py --help
```

### 2. 高機能表示ツール `view_firestore_data.py`

**基本使用方法:**

```bash
# 全データ表示
python view_firestore_data.py

# ユーザー情報のみ
python view_firestore_data.py --users

# 勤怠データのみ
python view_firestore_data.py --attendance

# セッション情報のみ
python view_firestore_data.py --sessions

# サマリーのみ
python view_firestore_data.py --summary

# JSONエクスポート
python view_firestore_data.py --export [ファイル名]
```

## 📋 現在のデータ構造

### ユーザーデータ

- **jpz4149**: 個人の打刻記録（2 件）
- **統合勤怠データ**: 移行された従来データ（31 件）

### 勤怠記録項目

- 📅 **日付**: 2025-07-01 ～ 2025-07-31
- ⏰ **出勤時刻**: check_in
- 🏠 **退勤時刻**: check_out
- 💼 **実働時間**: actual
- 🕘 **残業時間**: overtime
- ☕ **休憩時間**: break
- 💰 **交通費**: travel_cost
- 🚉 **出発地**: travel_from
- 🏢 **到着地**: travel_to
- 📝 **備考**: notes

## 📊 データサマリー (現在)

```
✅ Firestore接続: 成功
🌐 プロジェクト: highflat-attendance
📊 データユーザー数: 2
📈 総記録数: 33件

👤 jpz4149: 2件
   📋 最新記録: 2025-07-10 出勤 18:15

👤 統合勤怠データ: 31件
   📅 期間: 2025-07-01 ～ 2025-07-31
   ⏰ 出勤記録: 18日分
   💰 交通費記録: 1件（¥465）
```

## 🔧 データ管理コマンド

### 環境変数の設定

```bash
export USE_FIRESTORE=true
export FIREBASE_PROJECT_ID=highflat-attendance
export GOOGLE_APPLICATION_CREDENTIALS=./firebase-service-account.json
```

### アプリケーション起動

```bash
# Firestoreアプリケーション起動
python app_firestore.py

# 従来版アプリケーション起動
python app.py
```

### データバックアップ

```bash
# 整理されたデータをエクスポート
python simple_firestore_viewer.py --export backup_$(date +%Y%m%d).json

# 全Firestoreデータをエクスポート
python view_firestore_data.py --export raw_backup_$(date +%Y%m%d).json
```

## 📈 データ分析例

### 月別統計確認

```bash
# 2025年7月の勤怠サマリー
python simple_firestore_viewer.py --detailed | grep "2025-07"
```

### 特定ユーザーのデータ確認

```bash
# jpz4149のデータを確認
python view_firestore_data.py --users | grep -A 5 "jpz4149"
```

### 交通費データの確認

```bash
# 交通費記録を確認
python simple_firestore_viewer.py --detailed | grep -v "   --" | grep "465"
```

## 🌐 Firebase Console でのデータ確認

1. [Firebase Console](https://console.firebase.google.com/) にアクセス
2. プロジェクト `highflat-attendance` を選択
3. 左メニューの「Firestore Database」をクリック
4. 以下のコレクションが表示されます：
   - `user_attendance` - 勤怠データ（12 ドキュメント）
   - `users` - ユーザー情報（0 ドキュメント）
   - `user_sessions` - セッション情報（0 ドキュメント）

## 📝 データ形式の説明

### 移行されたデータ構造

従来の Firebase Realtime Database から移行されたデータは以下の形式で保存されています：

```json
{
  "統合勤怠データ": {
    "2025-07-01": {
      "check_in": "15:15",
      "break": 1.0
    },
    "2025-07-08": {
      "check_in": "19:15",
      "travel_cost": 465,
      "travel_from": "南砂",
      "travel_to": "四谷"
    }
  }
}
```

### 新しいデータ構造

新規作成されるデータは以下の形式です：

```json
{
  "jpz4149": {
    "2025-07-10": {
      "check_in": "18:15"
    }
  }
}
```

## 🚀 次のステップ

1. **データクリーンアップ**: 統合データを適切なユーザーに割り当て
2. **ユーザー管理**: users コレクションへの正式なユーザー登録
3. **セキュリティ**: アクセス権限とセキュリティルールの設定
4. **バックアップ**: 定期的な自動バックアップの設定

## 🔗 関連ファイル

- `simple_firestore_viewer.py` - シンプル表示ツール
- `view_firestore_data.py` - 高機能表示ツール
- `firestore_config.py` - Firestore 接続管理
- `app_firestore.py` - Firestore アプリケーション
- `FIRESTORE_SETUP.md` - セットアップガイド
- `MIGRATION_GUIDE.md` - 移行ガイド

---

**📞 サポート**: データ管理や分析でご不明な点がございましたら、ツールのヘルプオプション（`--help`）をご参照ください。
