# Vercel デプロイ手順

## 前提条件

- GitHub アカウント
- Vercel アカウント（GitHub でサインアップ可能）

## デプロイ手順

### 1. GitHub にリポジトリをプッシュ

```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/yourusername/your-repo-name.git
git push -u origin main
```

### 2. Vercel でデプロイ

1. [Vercel](https://vercel.com)にアクセス
2. GitHub でサインイン
3. "New Project"をクリック
4. GitHub リポジトリを選択
5. 以下の設定でデプロイ：
   - Framework Preset: Other
   - Root Directory: ./
   - Build Command: 空欄
   - Output Directory: 空欄
   - Install Command: `pip install -r requirements.txt`

### 3. 環境変数の設定（必要に応じて）

Vercel のプロジェクト設定で環境変数を追加できます。

## 注意事項

- Vercel はサーバーレス環境のため、ファイルシステムへの書き込みは一時的です
- 生成された Excel ファイルや JSON データは、デプロイ後にリセットされます
- 本格的な運用には、データベース（PostgreSQL 等）の使用を推奨します

## トラブルシューティング

- デプロイエラーが発生した場合は、Vercel のログを確認
- Python バージョンの問題がある場合は、`runtime.txt`で指定可能
