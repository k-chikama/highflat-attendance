#!/usr/bin/env python3
"""
Vercel デプロイヘルパー
Firebase Service Account Key の Base64 エンコードとVercelデプロイの支援
"""

import base64
import json
import os
import sys
from pathlib import Path

def print_header(title):
    """ヘッダーを表示"""
    print(f"\n{'=' * 60}")
    print(f"🚀 {title}")
    print(f"{'=' * 60}")

def print_step(step_num, title):
    """ステップを表示"""
    print(f"\n📋 Step {step_num}: {title}")
    print("-" * 40)

def encode_firebase_key():
    """Firebase Service Account Key をBase64エンコード"""
    key_file = Path("firebase-service-account.json")
    
    if not key_file.exists():
        print("❌ firebase-service-account.json が見つかりません")
        print("\n📋 Firebase Service Account Key の取得方法:")
        print("1. Firebase Console (https://console.firebase.google.com/) にアクセス")
        print("2. highflat-attendance プロジェクトを選択")
        print("3. Project Settings → Service accounts")
        print("4. 'Generate new private key' をクリック")
        print("5. ダウンロードしたファイルを firebase-service-account.json として保存")
        return None
    
    try:
        with open(key_file, 'r', encoding='utf-8') as f:
            key_data = f.read()
        
        # JSONの妥当性チェック
        json.loads(key_data)
        
        # Base64エンコード
        encoded_key = base64.b64encode(key_data.encode('utf-8')).decode('ascii')
        
        print("✅ Firebase Service Account Key のBase64エンコード完了")
        print(f"📄 文字数: {len(encoded_key)} 文字")
        
        return encoded_key
    
    except json.JSONDecodeError:
        print("❌ firebase-service-account.json が有効なJSONファイルではありません")
        return None
    except Exception as e:
        print(f"❌ エラー: {str(e)}")
        return None

def save_env_vars(encoded_key):
    """環境変数をファイルに保存"""
    env_vars = [
        "USE_FIRESTORE=true",
        "FIREBASE_PROJECT_ID=highflat-attendance",
        f"GOOGLE_APPLICATION_CREDENTIALS_BASE64={encoded_key}"
    ]
    
    env_file = Path("vercel-env-vars.txt")
    with open(env_file, 'w', encoding='utf-8') as f:
        f.write("# Vercel Environment Variables\n")
        f.write("# コピーしてVercel ダッシュボードに設定してください\n\n")
        for var in env_vars:
            f.write(f"{var}\n")
    
    print(f"💾 環境変数を {env_file} に保存しました")

def print_deploy_instructions():
    """デプロイ手順を表示"""
    print_step(1, "Vercel プロジェクト作成")
    print("1. https://vercel.com にアクセス")
    print("2. 'New Project' をクリック")
    print("3. 'k-chikama/highflat-attendance' リポジトリを選択")
    print("4. 'Import' をクリック")
    
    print_step(2, "環境変数設定")
    print("1. Vercel プロジェクト画面で 'Settings' タブをクリック")
    print("2. 'Environment Variables' セクションを選択")
    print("3. 以下の環境変数を設定:")
    print("   - USE_FIRESTORE = true")
    print("   - FIREBASE_PROJECT_ID = highflat-attendance")
    print("   - GOOGLE_APPLICATION_CREDENTIALS_BASE64 = [上記のBase64文字列]")
    
    print_step(3, "デプロイ実行")
    print("1. 'Deploy' ボタンをクリック")
    print("2. ビルド完了まで待機（約2-3分）")
    print("3. 提供されたURLでアクセス確認")
    
    print_step(4, "動作確認")
    print("1. 認証画面が表示されることを確認")
    print("2. ユーザー登録・ログインをテスト")
    print("3. 勤怠打刻機能をテスト")
    print("4. Excel出力機能をテスト")

def print_troubleshooting():
    """トラブルシューティング"""
    print_header("🔧 トラブルシューティング")
    
    print("\n❌ よくある問題と解決方法:")
    print("\n1. Module 'google-cloud-firestore' not found")
    print("   → requirements.txt に依存関係が含まれているか確認")
    
    print("\n2. Firebase認証エラー")
    print("   → GOOGLE_APPLICATION_CREDENTIALS_BASE64 の設定を確認")
    print("   → Base64エンコードに改行が含まれていないか確認")
    
    print("\n3. Firestore接続エラー")
    print("   → Firebase Console でFirestore APIが有効になっているか確認")
    print("   → Service Account に適切な権限があるか確認")
    
    print("\n4. ビルドエラー")
    print("   → Vercel ビルドログを確認")
    print("   → Python バージョンが 3.9+ であることを確認")

def main():
    """メイン処理"""
    print_header("Vercel デプロイヘルパー")
    
    # Firebase Service Account Key のエンコード
    print_step(1, "Firebase Service Account Key の準備")
    encoded_key = encode_firebase_key()
    
    if not encoded_key:
        print("\n❌ Firebase Service Account Key の準備に失敗しました")
        print("上記の手順に従ってキーファイルを準備してから再実行してください")
        return 1
    
    # 環境変数ファイルの保存
    save_env_vars(encoded_key)
    
    # デプロイ手順の表示
    print_deploy_instructions()
    
    # Base64文字列の表示（セキュリティのため最初と最後のみ）
    print_header("📋 環境変数設定用 Base64 文字列")
    preview = f"{encoded_key[:50]}...{encoded_key[-50:]}"
    print(f"GOOGLE_APPLICATION_CREDENTIALS_BASE64={preview}")
    print(f"📏 全体の長さ: {len(encoded_key)} 文字")
    print("\n💾 完全な文字列は vercel-env-vars.txt ファイルに保存されています")
    
    # トラブルシューティング
    print_troubleshooting()
    
    print_header("🎉 準備完了")
    print("Vercel ダッシュボードで環境変数を設定してデプロイを実行してください！")
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 