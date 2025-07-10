# Web 勤怠システム

Flask + openpyxl で作成された Web 勤怠システムです。

## 機能

- 勤怠打刻（出勤・退勤）
- 勤怠入力・編集
- 勤怠情報表示
- Excel 出力
- 祝日対応
- 交通費・駅名列
- 即時保存
- 本日行の強調表示

## ローカル環境での実行

### 前提条件

- Python 3.8 以上
- pip

### セットアップ

```bash
# 仮想環境を作成
python3 -m venv .venv

# 仮想環境を有効化
source .venv/bin/activate  # macOS/Linux
# .venv\Scripts\activate  # Windows

# 依存関係をインストール
pip install -r requirements.txt

# アプリケーションを実行
python app.py
```

### アクセス

- http://localhost:5001

## Vercel 環境でのデプロイ

### データ永続化の問題

Vercel はサーバーレス環境のため、ファイルシステムへの書き込みは永続化されません。このシステムでは GitHub Gist を使用してデータを永続化しています。

### セットアップ手順

#### 1. GitHub Personal Access Token の作成

1. GitHub にログイン
2. Settings > Developer settings > Personal access tokens > Tokens (classic)
3. "Generate new token" をクリック
4. 以下の権限を選択：
   - `gist` (Gist の作成・編集)
5. トークンを生成し、安全な場所に保存

#### 2. GitHub Gist の作成

1. GitHub で新しい Gist を作成
2. ファイル名: `attendance_data.json`
3. 内容: `{}`
4. "Create secret gist" をクリック
5. Gist の URL から ID を取得（例: `https://gist.github.com/username/1234567890abcdef` → `1234567890abcdef`）

#### 3. Vercel プロジェクトの作成

1. Vercel にログイン
2. "New Project" をクリック
3. GitHub リポジトリを選択
4. 以下の環境変数を設定：
   - `GIST_ID`: 作成した Gist の ID
   - `GITHUB_TOKEN`: 作成した Personal Access Token

#### 4. デプロイ

1. "Deploy" をクリック
2. デプロイ完了後、提供された URL でアクセス

### 環境変数の設定

Vercel のダッシュボードで以下の環境変数を設定してください：

```
GIST_ID=your_gist_id_here
GITHUB_TOKEN=your_github_token_here
```

### トラブルシューティング

#### 打刻が反映されない

1. 環境変数が正しく設定されているか確認
2. GitHub Personal Access Token の権限を確認
3. Gist ID が正しいか確認
4. Vercel のログでエラーを確認

#### jpholiday エラー

- Vercel は Python 3.9 を使用
- requirements.txt で jpholiday==1.0.2 を指定済み
- 型エラーが発生した場合は土日のみの判定にフォールバック

#### その他の問題

- Vercel のダッシュボードでログを確認
- GitHub API の制限に達していないか確認

## ファイル構成

```
highflat/
├── app.py                 # メインアプリケーション
├── wsgi.py               # Vercel用WSGIエントリーポイント
├── requirements.txt      # Python依存関係
├── runtime.txt          # Pythonバージョン指定
├── vercel.json          # Vercel設定
├── templates/           # HTMLテンプレート
│   ├── base.html
│   ├── punch.html
│   ├── attendance.html
│   └── attendance_info.html
├── static/              # 静的ファイル
│   ├── css/
│   └── js/
└── attendance_data.json # 勤怠データ（ローカル環境）
```

## 技術仕様

- **フレームワーク**: Flask 2.3.3
- **データ形式**: JSON
- **Excel 出力**: openpyxl 3.1.2
- **祝日判定**: jpholiday 1.0.2
- **データ永続化**: GitHub Gist API（Vercel 環境）
- **フロントエンド**: Bootstrap 5, JavaScript

## ライセンス

MIT License
