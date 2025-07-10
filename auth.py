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