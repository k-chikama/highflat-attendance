#!/usr/bin/env python3
"""
Firestore統合のテストスクリプト
実際のFirestore接続を必要としないローカルテスト用
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_firestore_imports():
    """Firestore関連のインポートテスト"""
    try:
        from firestore_config import firestore_manager
        print("✓ firestore_config インポート成功")
        
        from auth_firestore import firestore_auth_manager, firestore_login_required
        print("✓ auth_firestore インポート成功")
        
        from attendance_firestore import firestore_attendance_manager
        print("✓ attendance_firestore インポート成功")
        
        return True
    except Exception as e:
        print(f"✗ インポートエラー: {e}")
        return False

def test_firestore_manager_initialization():
    """FirestoreManager初期化テスト"""
    try:
        from firestore_config import firestore_manager
        
        # 初期化状態チェック
        print(f"Firestore利用可能: {firestore_manager.is_available()}")
        
        if not firestore_manager.is_available():
            print("⚠ Firestore認証情報が設定されていません（開発環境では正常）")
        else:
            print("✓ Firestore初期化成功")
        
        return True
    except Exception as e:
        print(f"✗ FirestoreManager初期化エラー: {e}")
        return False

def test_auth_manager_methods():
    """AuthManager機能テスト"""
    try:
        from auth_firestore import firestore_auth_manager
        
        # メソッドの存在確認
        methods = [
            'hash_password', 'verify_password', 'login_user', 'logout_user',
            'is_logged_in', 'get_current_user', 'get_current_display_name',
            'add_user', 'delete_user', 'get_user_list'
        ]
        
        for method in methods:
            if hasattr(firestore_auth_manager, method):
                print(f"✓ {method} メソッド存在")
            else:
                print(f"✗ {method} メソッド不在")
                return False
        
        # パスワードハッシュテスト
        test_password = "test123"
        hashed = firestore_auth_manager.hash_password(test_password)
        if hashed and len(hashed) == 64:  # SHA256は64文字
            print("✓ パスワードハッシュ化正常")
        else:
            print("✗ パスワードハッシュ化異常")
            return False
        
        return True
    except Exception as e:
        print(f"✗ AuthManager機能テストエラー: {e}")
        return False

def test_attendance_manager_methods():
    """AttendanceManager機能テスト"""
    try:
        from attendance_firestore import firestore_attendance_manager
        
        # メソッドの存在確認
        methods = [
            'load_attendance_cache', 'save_attendance_data',
            'get_user_attendance_data', 'update_user_attendance_data',
            'get_user_monthly_data', 'get_all_users_data',
            'migrate_from_legacy_format', 'backup_to_json', 'restore_from_json'
        ]
        
        for method in methods:
            if hasattr(firestore_attendance_manager, method):
                print(f"✓ {method} メソッド存在")
            else:
                print(f"✗ {method} メソッド不在")
                return False
        
        # キャッシュ初期化確認
        if hasattr(firestore_attendance_manager, 'attendance_cache'):
            print("✓ attendance_cache 初期化済み")
        else:
            print("✗ attendance_cache 未初期化")
            return False
        
        return True
    except Exception as e:
        print(f"✗ AttendanceManager機能テストエラー: {e}")
        return False

def test_app_firestore_imports():
    """app_firestore.py インポートテスト"""
    try:
        # Flask アプリケーションのインポート確認
        import app_firestore
        print("✓ app_firestore インポート成功")
        
        # 主要関数の存在確認
        functions = [
            'get_auth_manager', 'get_attendance_manager',
            'get_login_required_decorator', 'load_user_data', 'save_user_data'
        ]
        
        for func in functions:
            if hasattr(app_firestore, func):
                print(f"✓ {func} 関数存在")
            else:
                print(f"✗ {func} 関数不在")
                return False
        
        return True
    except Exception as e:
        print(f"✗ app_firestore インポートエラー: {e}")
        return False

def test_environment_variables():
    """環境変数テスト"""
    print("\n=== 環境変数確認 ===")
    
    env_vars = [
        'USE_FIRESTORE',
        'FIREBASE_PROJECT_ID',
        'GOOGLE_APPLICATION_CREDENTIALS',
        'FIREBASE_SERVICE_ACCOUNT_JSON'
    ]
    
    for var in env_vars:
        value = os.environ.get(var)
        if value:
            if var == 'FIREBASE_SERVICE_ACCOUNT_JSON':
                print(f"✓ {var}: 設定済み（{len(value)}文字）")
            else:
                print(f"✓ {var}: {value}")
        else:
            print(f"- {var}: 未設定")
    
    print()

def run_all_tests():
    """全テストを実行"""
    print("=== Firestore統合テスト開始 ===\n")
    
    test_environment_variables()
    
    tests = [
        ("インポートテスト", test_firestore_imports),
        ("FirestoreManager初期化テスト", test_firestore_manager_initialization),
        ("AuthManager機能テスト", test_auth_manager_methods),
        ("AttendanceManager機能テスト", test_attendance_manager_methods),
        ("app_firestore インポートテスト", test_app_firestore_imports),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        if test_func():
            passed += 1
            print(f"✓ {test_name} 成功")
        else:
            print(f"✗ {test_name} 失敗")
    
    print(f"\n=== テスト結果: {passed}/{total} 成功 ===")
    
    if passed == total:
        print("🎉 すべてのテストが成功しました！")
        print("\n次のステップ:")
        print("1. Firebase Console でプロジェクトを作成")
        print("2. サービスアカウントキーを取得")
        print("3. 環境変数を設定")
        print("4. python app_firestore.py で起動")
    else:
        print("⚠ 一部のテストが失敗しました。設定を確認してください。")
    
    return passed == total

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1) 