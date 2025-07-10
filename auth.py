import hashlib
import secrets
from functools import wraps
from flask import session, request, redirect, url_for, jsonify
import os

class AuthManager:
    def __init__(self):
        # 環境変数から管理者アカウントを取得（デフォルト値あり）
        self.admin_users = {
            os.environ.get('ADMIN_USERNAME', 'admin'): self.hash_password(os.environ.get('ADMIN_PASSWORD', 'admin123'))
        }
        
        # 追加ユーザー（環境変数で設定可能）
        additional_users = os.environ.get('ADDITIONAL_USERS', '')
        if additional_users:
            # 形式: "user1:pass1,user2:pass2"
            for user_pass in additional_users.split(','):
                if ':' in user_pass:
                    username, password = user_pass.strip().split(':', 1)
                    self.admin_users[username] = self.hash_password(password)
        
        # データベースから保存されたユーザー情報を読み込み
        self.load_users_from_database()
    
    def hash_password(self, password: str) -> str:
        """パスワードをハッシュ化"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def verify_password(self, username: str, password: str) -> bool:
        """ユーザー認証"""
        if username in self.admin_users:
            return self.admin_users[username] == self.hash_password(password)
        return False
    
    def login_user(self, username: str) -> bool:
        """ユーザーをログイン状態にする"""
        if username in self.admin_users:
            session['logged_in'] = True
            session['username'] = username
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
    
    def get_user_list(self) -> list:
        """登録ユーザー一覧を取得"""
        return list(self.admin_users.keys())
    
    def add_user(self, username: str, password: str) -> bool:
        """新規ユーザーを追加"""
        if username in self.admin_users:
            return False  # ユーザーが既に存在
        
        self.admin_users[username] = self.hash_password(password)
        # ユーザー情報をFirebaseに保存
        self.save_users_to_database()
        return True
    
    def delete_user(self, username: str) -> bool:
        """ユーザーを削除"""
        # 環境変数で設定されたデフォルトユーザーは削除不可
        default_admin = os.environ.get('ADMIN_USERNAME', 'admin')
        if username == default_admin:
            return False
        
        if username in self.admin_users:
            del self.admin_users[username]
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
                    'users_auth': self.admin_users
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
                    # 環境変数のユーザーとマージ
                    stored_users = data['users_auth']
                    for username, password_hash in stored_users.items():
                        if username not in self.admin_users:
                            self.admin_users[username] = password_hash
                    print("DEBUG: Firebaseからユーザー情報を読み込み")
        except Exception as e:
            print(f"ERROR: ユーザー情報読み込み失敗 - {str(e)}")
    
    def is_admin(self, username: str) -> bool:
        """管理者権限チェック（デフォルトユーザーのみ管理者）"""
        default_admin = os.environ.get('ADMIN_USERNAME', 'admin')
        return username == default_admin

# グローバルインスタンス
auth_manager = AuthManager()

def login_required(f):
    """ログイン必須デコレータ"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not auth_manager.is_logged_in():
            if request.is_json:
                return jsonify({'success': False, 'error': 'Authentication required'}), 401
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """管理者権限必須デコレータ"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not auth_manager.is_logged_in():
            if request.is_json:
                return jsonify({'success': False, 'error': 'Authentication required'}), 401
            return redirect(url_for('login'))
        
        current_user = auth_manager.get_current_user()
        if not auth_manager.is_admin(current_user):
            if request.is_json:
                return jsonify({'success': False, 'error': 'Admin privileges required'}), 403
            return redirect(url_for('index'))
        
        return f(*args, **kwargs)
    return decorated_function 