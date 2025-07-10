import hashlib
import secrets
from functools import wraps
from flask import session, request, redirect, url_for, jsonify
import os

class AuthManager:
    def __init__(self):
        # ユーザー辞書（デフォルトは空）
        self.users = {}
        # ユーザー表示名辞書（username -> display_name）
        self.user_display_names = {}
        
        # データベースから保存されたユーザー情報を読み込み
        self.load_users_from_database()
    
    def hash_password(self, password: str) -> str:
        """パスワードをハッシュ化"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def verify_password(self, username: str, password: str) -> bool:
        """ユーザー認証"""
        if username in self.users:
            return self.users[username] == self.hash_password(password)
        return False
    
    def login_user(self, username: str) -> bool:
        """ユーザーをログイン状態にする"""
        if username in self.users:
            session['logged_in'] = True
            session['username'] = username
            session['display_name'] = self.user_display_names.get(username, username)
            session['session_id'] = secrets.token_hex(16)
            return True
        return False
    
    def logout_user(self):
        """ユーザーをログアウト"""
        session.clear()
    
    def is_logged_in(self) -> bool:
        """ログイン状態チェック"""
        return session.get('logged_in', False)
    
    def get_current_user(self) -> str:
        """現在のユーザー名を取得"""
        return session.get('username', '')
    
    def get_current_display_name(self) -> str:
        """現在のユーザーの表示名を取得"""
        return session.get('display_name', session.get('username', ''))
    
    def get_user_list(self) -> list:
        """登録ユーザー一覧を取得"""
        return list(self.users.keys())
    
    def add_user(self, username: str, password: str, display_name: str = '') -> bool:
        """新規ユーザーを追加"""
        if username in self.users:
            return False  # ユーザーが既に存在
        
        self.users[username] = self.hash_password(password)
        # 表示名が指定されていない場合はユーザー名を使用
        self.user_display_names[username] = display_name or username
        
        # ユーザー情報をFirebaseに保存
        self.save_users_to_database()
        return True
    
    def delete_user(self, username: str) -> bool:
        """ユーザーを削除"""
        if username in self.users:
            del self.users[username]
            if username in self.user_display_names:
                del self.user_display_names[username]
            self.save_users_to_database()
            return True
        return False
    
    def save_users_to_database(self):
        """ユーザー情報をデータベースに保存"""
        try:
            from firebase_config import firebase_db
            if firebase_db.is_available():
                # Firebaseにユーザー情報を保存
                user_data = {
                    'users_auth': self.users,
                    'user_display_names': self.user_display_names
                }
                firebase_db.save_data(user_data)
                print("DEBUG: ユーザー情報をFirebaseに保存")
        except Exception as e:
            print(f"ERROR: ユーザー情報保存失敗 - {str(e)}")
    
    def load_users_from_database(self):
        """データベースからユーザー情報を読み込み"""
        try:
            from firebase_config import firebase_db
            if firebase_db.is_available():
                data = firebase_db.load_data()
                if 'users_auth' in data:
                    # 保存されたユーザー情報を読み込み
                    self.users = data['users_auth']
                    print("DEBUG: Firebaseからユーザー情報を読み込み")
                if 'user_display_names' in data:
                    # 保存されたユーザー表示名を読み込み
                    self.user_display_names = data['user_display_names']
                    print("DEBUG: Firebaseからユーザー表示名を読み込み")
        except Exception as e:
            print(f"ERROR: ユーザー情報読み込み失敗 - {str(e)}")

# グローバルインスタンス
auth_manager = AuthManager()

def login_required(f):
    """ログイン必須デコレータ"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not auth_manager.is_logged_in():
            if request.is_json:
                return jsonify({'success': False, 'error': 'Authentication required'}), 401
            return redirect(url_for('auth'))
        return f(*args, **kwargs)
    return decorated_function 