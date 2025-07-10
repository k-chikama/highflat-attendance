#!/usr/bin/env python3
"""
Vercel デプロイ準備ヘルパー
"""

import os
import base64
import json

def encode_service_account():
    """Firebase Service Accountキーをbase64エンコード"""
    key_file = 'firebase-service-account.json'
    
    if not os.path.exists(key_file):
        print(f"❌ {key_file} が見つかりません")
        print("Firebase Console からサービスアカウントキーをダウンロードしてください")
        return
    
    try:
        with open(key_file, 'r') as f:
            content = f.read()
        
        # Base64エンコード
        encoded = base64.b64encode(content.encode('utf-8')).decode('utf-8')
        
        print("✅ Firebase Service Account キーのBase64エンコードが完了しました")
        print("\n📋 Vercelの環境変数に以下を設定してください:")
        print("=" * 60)
        print("USE_FIRESTORE=true")
        print(f"FIREBASE_PROJECT_ID=highflat-attendance")
        print(f"GOOGLE_APPLICATION_CREDENTIALS_BASE64={encoded}")
        print("=" * 60)
        
        # ファイルに保存
        with open('vercel-env-vars.txt', 'w') as f:
            f.write("# Vercel環境変数設定\n")
            f.write("USE_FIRESTORE=true\n")
            f.write("FIREBASE_PROJECT_ID=highflat-attendance\n")
            f.write(f"GOOGLE_APPLICATION_CREDENTIALS_BASE64={encoded}\n")
        
        print("\n💾 環境変数を 'vercel-env-vars.txt' に保存しました")
        
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")

def verify_requirements():
    """requirements.txtの確認"""
    print("\n🔍 requirements.txt の確認...")
    
    required_packages = [
        'google-cloud-firestore',
        'firebase-admin',
        'flask',
        'openpyxl',
        'bcrypt'
    ]
    
    try:
        with open('requirements.txt', 'r') as f:
            content = f.read().lower()
        
        missing = []
        for package in required_packages:
            if package.lower() not in content:
                missing.append(package)
        
        if missing:
            print(f"❌ 不足しているパッケージ: {', '.join(missing)}")
        else:
            print("✅ 必要なパッケージがすべて含まれています")
            
    except FileNotFoundError:
        print("❌ requirements.txt が見つかりません")

def check_git_status():
    """Gitの状態確認"""
    print("\n📋 デプロイチェックリスト:")
    print("=" * 40)
    
    # ファイル存在確認
    files_to_check = [
        'wsgi.py',
        'vercel.json', 
        'app_firestore.py',
        'firestore_config.py',
        'auth_firestore.py',
        'attendance_firestore.py'
    ]
    
    for file in files_to_check:
        status = "✅" if os.path.exists(file) else "❌"
        print(f"{status} {file}")
    
    print("\n🚀 デプロイ手順:")
    print("1. ✅ Firebase Service Account キー準備完了")
    print("2. ⏳ Vercel環境変数設定")
    print("3. ⏳ Vercelデプロイ実行")
    print("4. ⏳ 動作確認")

if __name__ == "__main__":
    print("🚀 Vercel デプロイ準備")
    print("=" * 50)
    
    encode_service_account()
    verify_requirements()
    check_git_status()
    
    print("\n📖 詳細な手順は VERCEL_FIRESTORE_DEPLOY.md を参照してください") 