#!/usr/bin/env python3
"""
Firestoreから特定のユーザーを削除するスクリプト
"""

import os
import sys
from firestore_config import FirestoreManager
from auth_firestore import FirestoreAuthManager

def delete_user_from_firestore(username):
    """Firestoreから指定されたユーザーを削除"""
    
    # 環境変数の設定確認
    if not os.environ.get('USE_FIRESTORE'):
        os.environ['USE_FIRESTORE'] = 'true'
    if not os.environ.get('FIREBASE_PROJECT_ID'):
        os.environ['FIREBASE_PROJECT_ID'] = 'highflat-attendance'
    if not os.environ.get('GOOGLE_APPLICATION_CREDENTIALS'):
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = './firebase-service-account.json'
    
    # Firestore接続
    firestore_manager = FirestoreManager()
    if not firestore_manager.is_available():
        print("❌ Firestore接続に失敗しました")
        return False
    
    # FirestoreAuthManager初期化
    auth_manager = FirestoreAuthManager()
    
    try:
        print(f"🔍 ユーザー '{username}' の削除を開始...")
        
        # 1. ユーザー情報を削除
        users_result = firestore_manager.delete_document('users', username)
        print(f"✅ ユーザー情報削除: {users_result}")
        
        # 2. ユーザーのセッションを削除
        sessions_docs = firestore_manager.get_collection('user_sessions')
        deleted_sessions = 0
        if sessions_docs:
            for session_doc in sessions_docs:
                if session_doc.get('username') == username:
                    session_id = session_doc.get('session_id')
                    if session_id:
                        firestore_manager.delete_document('user_sessions', session_id)
                        deleted_sessions += 1
        
        print(f"✅ セッション削除: {deleted_sessions}件")
        
        # 3. ユーザーの勤怠データを削除
        attendance_result = firestore_manager.delete_document('user_attendance', username)
        print(f"✅ 勤怠データ削除: {attendance_result}")
        
        # 4. キャッシュをリフレッシュ
        auth_manager.load_users_cache()
        
        print(f"🎉 ユーザー '{username}' の削除が完了しました")
        return True
        
    except Exception as e:
        print(f"❌ エラー: {str(e)}")
        return False

def main():
    if len(sys.argv) != 2:
        print("使用方法: python delete_user.py <ユーザー名>")
        print("例: python delete_user.py jpz4149")
        return
    
    username = sys.argv[1]
    
    # 確認
    response = input(f"本当にユーザー '{username}' を削除しますか？ (y/N): ")
    if response.lower() != 'y':
        print("キャンセルしました")
        return
    
    # 削除実行
    success = delete_user_from_firestore(username)
    
    if success:
        print(f"\n✅ ユーザー '{username}' の削除が完了しました")
        print("これでVercel環境で同じユーザー名で新規登録できます")
    else:
        print(f"\n❌ ユーザー '{username}' の削除に失敗しました")

if __name__ == "__main__":
    main() 