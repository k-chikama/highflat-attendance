#!/usr/bin/env python3
"""
勤怠データ構造修正スクリプト
古いグローバルデータ構造を新しいユーザー別データ構造に修正
"""

import json
import os
from datetime import datetime

def fix_attendance_data_structure():
    """勤怠データ構造を修正"""
    data_file = 'attendance_data.json'
    
    if not os.path.exists(data_file):
        print(f"❌ {data_file} が見つかりません")
        return False
    
    try:
        # 現在のデータを読み込み
        with open(data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print("🔍 現在のデータ構造を分析中...")
        
        # 正しいユーザー別データを保持
        user_data = {}
        
        # 既存のユーザー別データを保持
        for key, value in data.items():
            if key in ['testuser', 'jpz4149'] and isinstance(value, dict):
                user_data[key] = value
                print(f"✅ ユーザー {key} のデータを保持")
        
        # 古いグローバルデータを削除対象として特定
        global_keys_to_remove = [
            'actual', 'break', 'check', 'check_in', 'check_out', 
            'notes', 'overtime', 'travel_cost', 'travel_from', 
            'travel_to', 'work'
        ]
        
        removed_keys = []
        for key in global_keys_to_remove:
            if key in data:
                removed_keys.append(key)
        
        # バックアップを作成
        backup_file = f"{data_file}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        with open(backup_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"📁 バックアップ作成: {backup_file}")
        
        # 修正されたデータを保存
        with open(data_file, 'w', encoding='utf-8') as f:
            json.dump(user_data, f, ensure_ascii=False, indent=2)
        
        print("✅ データ構造修正完了")
        print(f"📊 保持されたユーザー: {list(user_data.keys())}")
        print(f"🗑️  削除されたグローバルキー: {removed_keys}")
        
        return True
        
    except Exception as e:
        print(f"❌ データ構造修正失敗: {str(e)}")
        return False

if __name__ == "__main__":
    print("🔧 勤怠データ構造修正スクリプト")
    print("=" * 50)
    
    success = fix_attendance_data_structure()
    
    if success:
        print("\n🎉 修正完了！")
        print("アプリケーションを再起動してください。")
    else:
        print("\n❌ 修正に失敗しました。") 