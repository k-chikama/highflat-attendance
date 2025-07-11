#!/bin/bash
# Firebase Service Account Key準備確認とBase64エンコード

echo "🔐 Firebase Service Account Key準備チェック"
echo "================================================"

# ファイル存在チェック
if [ ! -f "firebase-service-account.json" ]; then
    echo "❌ firebase-service-account.json が見つかりません"
    echo ""
    echo "📋 Firebase Service Account Key の取得方法:"
    echo "1. https://console.firebase.google.com/ にアクセス"
    echo "2. highflat-attendance プロジェクトを選択"
    echo "3. ⚙️ → Project settings → Service accounts"
    echo "4. 'Generate new private key' をクリック"
    echo "5. ダウンロードしたファイルを firebase-service-account.json にリネーム"
    echo "6. このフォルダに保存"
    echo ""
    echo "ファイルを準備してから再実行してください。"
    exit 1
fi

echo "✅ firebase-service-account.json が見つかりました"

# JSONファイルの妥当性チェック
if ! python -m json.tool firebase-service-account.json > /dev/null 2>&1; then
    echo "❌ firebase-service-account.json が有効なJSONファイルではありません"
    exit 1
fi

echo "✅ JSONファイル形式が正しいです"

# Base64エンコード
echo "🔄 Base64エンコード実行中..."
BASE64_KEY=$(cat firebase-service-account.json | base64 | tr -d '\n')

if [ -z "$BASE64_KEY" ]; then
    echo "❌ Base64エンコードに失敗しました"
    exit 1
fi

echo "✅ Base64エンコード完了"
echo "📄 文字数: ${#BASE64_KEY} 文字"

# 環境変数ファイル作成
cat > vercel-env-vars.txt << EOF
# Vercel Environment Variables
# コピーしてVercel ダッシュボードに設定してください

USE_FIRESTORE=true
FIREBASE_PROJECT_ID=highflat-attendance
GOOGLE_APPLICATION_CREDENTIALS_BASE64=${BASE64_KEY}
EOF

echo "💾 環境変数を vercel-env-vars.txt に保存しました"

echo ""
echo "📋 Vercel設定手順:"
echo "================================================"
echo "1. https://vercel.com/dashboard にアクセス"
echo "2. 'New Project' → k-chikama/highflat-attendance を選択"
echo "3. Settings → Environment Variables で以下を設定:"
echo ""
echo "   Variable Name: USE_FIRESTORE"
echo "   Value: true"
echo ""
echo "   Variable Name: FIREBASE_PROJECT_ID"
echo "   Value: highflat-attendance"
echo ""
echo "   Variable Name: GOOGLE_APPLICATION_CREDENTIALS_BASE64"
echo "   Value: [vercel-env-vars.txt からコピー]"
echo ""
echo "4. 'Deploy' ボタンをクリック"
echo ""
echo "🎉 準備完了です！" 