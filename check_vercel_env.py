#!/usr/bin/env python3
"""
Vercel環境変数チェックスクリプト
"""

import subprocess
import json
import sys

def run_command(cmd):
    """コマンドを実行して結果を返す"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.stdout.strip(), result.stderr.strip(), result.returncode
    except Exception as e:
        return "", str(e), 1

def check_vercel_env():
    """Vercel環境変数をチェック"""
    print("🔍 Vercel環境変数をチェック中...")
    
    # Vercel環境変数を取得
    stdout, stderr, code = run_command("vercel env ls")
    
    if code != 0:
        print(f"❌ Vercel CLIエラー: {stderr}")
        return False
    
    print("📋 現在のVercel環境変数:")
    print(stdout)
    
    # 必要な環境変数をチェック
    required_vars = [
        "USE_FIRESTORE",
        "FIREBASE_PROJECT_ID", 
        "GOOGLE_APPLICATION_CREDENTIALS_BASE64"
    ]
    
    missing_vars = []
    for var in required_vars:
        if var not in stdout:
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ 不足している環境変数: {missing_vars}")
        return False
    else:
        print("✅ 必要な環境変数はすべて設定されています")
        return True

def main():
    """メイン処理"""
    print("🚀 Vercel環境変数チェック開始")
    
    if not check_vercel_env():
        print("\n❌ 環境変数に問題があります")
        print("\n🔧 修正方法:")
        print("1. vercel env add USE_FIRESTORE")
        print("2. vercel env add FIREBASE_PROJECT_ID")
        print("3. vercel env add GOOGLE_APPLICATION_CREDENTIALS_BASE64")
        sys.exit(1)
    
    print("\n✅ 環境変数チェック完了")
    print("\n🔄 次のステップ:")
    print("1. vercel --prod でデプロイ")
    print("2. ブラウザで新規登録をテスト")

if __name__ == "__main__":
    main() 