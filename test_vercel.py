#!/usr/bin/env python3
"""
Vercel環境でのデータ永続化テストスクリプト
"""

import os
import json
import requests
from datetime import datetime

# 環境変数の確認
GIST_ID = os.environ.get('GIST_ID')
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')
USE_GIST = bool(GIST_ID and GITHUB_TOKEN)

print(f"GIST_ID: {GIST_ID}")
print(f"GITHUB_TOKEN: {'設定済み' if GITHUB_TOKEN else '未設定'}")
print(f"USE_GIST: {USE_GIST}")

def load_data_from_gist():
    """GitHub Gistからデータを読み込む"""
    try:
        headers = {
            'Authorization': f'token {GITHUB_TOKEN}',
            'Accept': 'application/vnd.github.v3+json'
        }
        response = requests.get(f'https://api.github.com/gists/{GIST_ID}', headers=headers)
        print(f"Gist読み込みレスポンス: {response.status_code}")
        if response.status_code == 200:
            gist_data = response.json()
            files = gist_data.get('files', {})
            for filename, file_data in files.items():
                if filename == 'attendance_data.json':
                    content = file_data.get('content', '{}')
                    data = json.loads(content)
                    print(f"読み込んだデータ: {data}")
                    return data
        return {}
    except Exception as e:
        print(f"Gist読み込みエラー: {e}")
        return {}

def save_data_to_gist(data):
    """GitHub Gistにデータを保存する"""
    try:
        headers = {
            'Authorization': f'token {GITHUB_TOKEN}',
            'Accept': 'application/vnd.github.v3+json'
        }
        
        # 現在のGistを取得
        response = requests.get(f'https://api.github.com/gists/{GIST_ID}', headers=headers)
        print(f"Gist取得レスポンス: {response.status_code}")
        if response.status_code != 200:
            print(f"Gist取得エラー: {response.status_code}")
            return
        
        gist_data = response.json()
        files = gist_data.get('files', {})
        
        # ファイル内容を更新
        files['attendance_data.json'] = {
            'content': json.dumps(data, ensure_ascii=False, indent=2)
        }
        
        # Gistを更新
        update_data = {
            'files': files
        }
        
        response = requests.patch(
            f'https://api.github.com/gists/{GIST_ID}',
            headers=headers,
            json=update_data
        )
        
        print(f"Gist更新レスポンス: {response.status_code}")
        if response.status_code != 200:
            print(f"Gist更新エラー: {response.status_code}")
            
    except Exception as e:
        print(f"Gist保存エラー: {e}")

def test_data_persistence():
    """データ永続化のテスト"""
    print("\n=== データ永続化テスト ===")
    
    # テストデータ
    test_data = {
        '2025-07-08': {
            'check_in': '09:00',
            'check_out': '18:00',
            'notes': 'テストデータ'
        }
    }
    
    print(f"保存するデータ: {test_data}")
    
    # データを保存
    if USE_GIST:
        save_data_to_gist(test_data)
        print("Gistにデータを保存しました")
        
        # データを読み込み
        loaded_data = load_data_from_gist()
        print(f"読み込んだデータ: {loaded_data}")
        
        # 比較
        if test_data == loaded_data:
            print("✅ データ永続化テスト成功")
        else:
            print("❌ データ永続化テスト失敗")
    else:
        print("⚠️ Gist設定がありません。ローカルファイルシステムを使用します。")

if __name__ == "__main__":
    test_data_persistence() 