import hashlib
import secrets
from functools import wraps
from flask import session, request, redirect, url_for, jsonify
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)

class FirestoreAuthManager:
    """Firestore ベースの認証管理クラス"""
    
    def __init__(self):
        # Firestoreマネージャーをインポート
        from firestore_config import firestore_manager
        self.firestore = firestore_manager
        
        # コレクション名
        self.users_collection = 'users'
        self.user_sessions_collection = 'user_sessions'
        
        # メモリキャッシュ（パフォーマンス向上のため）
        self.users_cache = {}
        self.user_display_names_cache = {}
        
        # 初期化時にユーザー情報をロード
        self.load_users_cache()
    
    def hash_password(self, password: str) -> str:
        """パスワードをハッシュ化"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def load_users_cache(self):
        """Firestoreからユーザー情報をキャッシュに読み込み"""
        try:
            if not self.firestore.is_available():
                logger.warning("Firestore利用不可、ローカルキャッシュを使用")
                return
            
            # 全ユーザー情報を取得
            users_docs = self.firestore.get_collection(self.users_collection)
            
            self.users_cache = {}
            self.user_display_names_cache = {}
            
            for user_doc in users_docs:
                username = user_doc.get('username')
                password_hash = user_doc.get('password_hash')
                display_name = user_doc.get('display_name', username)
                
                if username and password_hash:
                    self.users_cache[username] = password_hash
                    self.user_display_names_cache[username] = display_name
            
            logger.info(f"ユーザーキャッシュロード完了: {len(self.users_cache)}ユーザー")
            
        except Exception as e:
            logger.error(f"ユーザーキャッシュロード失敗: {str(e)}")
    
    def save_user_to_firestore(self, username: str, password_hash: str, display_name: str) -> bool:
        """Firestoreにユーザー情報を保存"""
        try:
            if not self.firestore.is_available():
                logger.warning("Firestore利用不可、保存スキップ")
                return False
            
            user_data = {
                'username': username,
                'password_hash': password_hash,
                'display_name': display_name,
                'created_at': self.firestore.db.collection('_metadata').document('_').get().create_time if self.firestore.db else None
            }
            
            # ユーザー名をドキュメントIDとして使用
            result = self.firestore.create_document(
                self.users_collection, 
                username, 
                user_data
            )
            
            if result:
                logger.info(f"ユーザー保存成功: {username}")
                return True
            else:
                logger.error(f"ユーザー保存失敗: {username}")
                return False
                
        except Exception as e:
            logger.error(f"ユーザー保存例外: {str(e)}")
            return False
    
    def verify_password(self, username: str, password: str) -> bool:
        """ユーザー認証"""
        if username in self.users_cache:
            return self.users_cache[username] == self.hash_password(password)
        
        # キャッシュにない場合、Firestoreから直接取得
        try:
            user_doc = self.firestore.get_document(self.users_collection, username)
            if user_doc and user_doc.get('password_hash'):
                stored_hash = user_doc['password_hash']
                return stored_hash == self.hash_password(password)
        except Exception as e:
            logger.error(f"パスワード認証エラー: {str(e)}")
        
        return False
    
    def login_user(self, username: str) -> bool:
        """ユーザーをログイン状態にする"""
        # ユーザーの存在確認
        if username not in self.users_cache:
            user_doc = self.firestore.get_document(self.users_collection, username)
            if not user_doc:
                return False
        
        display_name = self.user_display_names_cache.get(username, username)
        session_id = secrets.token_hex(16)
        
        # セッション情報をセット
        session['logged_in'] = True
        session['username'] = username
        session['display_name'] = display_name
        session['session_id'] = session_id
        
        # セッション情報をFirestoreに保存（オプション）
        try:
            if self.firestore.is_available():
                session_data = {
                    'username': username,
                    'session_id': session_id,
                    'created_at': self.firestore.db.collection('_metadata').document('_').get().create_time if self.firestore.db else None
                }
                self.firestore.create_document(
                    self.user_sessions_collection,
                    session_id,
                    session_data
                )
        except Exception as e:
            logger.warning(f"セッション保存失敗: {str(e)}")
        
        return True
    
    def logout_user(self):
        """ユーザーをログアウト"""
        session_id = session.get('session_id')
        
        # Firestoreからセッション削除（オプション）
        if session_id and self.firestore.is_available():
            try:
                self.firestore.delete_document(self.user_sessions_collection, session_id)
            except Exception as e:
                logger.warning(f"セッション削除失敗: {str(e)}")
        
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
        return list(self.users_cache.keys())
    
    def add_user(self, username: str, password: str, display_name: str = '') -> bool:
        """新規ユーザーを追加"""
        if username in self.users_cache:
            return False  # ユーザーが既に存在
        
        # ユーザー情報をFirestoreに保存
        password_hash = self.hash_password(password)
        display_name = display_name or username
        
        if self.save_user_to_firestore(username, password_hash, display_name):
            # キャッシュを更新
            self.users_cache[username] = password_hash
            self.user_display_names_cache[username] = display_name
            return True
        
        return False
    
    def delete_user(self, username: str) -> bool:
        """ユーザーを削除"""
        if username not in self.users_cache:
            return False
        
        try:
            # Firestoreから削除
            if self.firestore.is_available():
                success = self.firestore.delete_document(self.users_collection, username)
                if success:
                    # キャッシュからも削除
                    del self.users_cache[username]
                    if username in self.user_display_names_cache:
                        del self.user_display_names_cache[username]
                    return True
            return False
            
        except Exception as e:
            logger.error(f"ユーザー削除失敗: {str(e)}")
            return False
    
    def update_user_display_name(self, username: str, new_display_name: str) -> bool:
        """ユーザーの表示名を更新"""
        if username not in self.users_cache:
            return False
        
        try:
            if self.firestore.is_available():
                success = self.firestore.update_document(
                    self.users_collection,
                    username,
                    {'display_name': new_display_name}
                )
                if success:
                    # キャッシュも更新
                    self.user_display_names_cache[username] = new_display_name
                    return True
            return False
            
        except Exception as e:
            logger.error(f"表示名更新失敗: {str(e)}")
            return False

# グローバルインスタンス
firestore_auth_manager = FirestoreAuthManager()

def firestore_login_required(f):
    """Firestore認証必須デコレータ"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not firestore_auth_manager.is_logged_in():
            if request.is_json:
                return jsonify({'success': False, 'error': 'Authentication required'}), 401
            return redirect(url_for('auth'))
        return f(*args, **kwargs)
    return decorated_function 