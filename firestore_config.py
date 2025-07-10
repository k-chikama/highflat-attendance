import os
import json
import logging
from typing import Dict, Any, Optional, List
from google.cloud import firestore
from google.oauth2 import service_account
import firebase_admin
from firebase_admin import credentials

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FirestoreManager:
    """Firebase Firestore データベース管理クラス"""
    
    def __init__(self):
        self.db = None
        self.app = None
        self.is_initialized = False
        
        # 初期化を試行
        self._initialize_firestore()
    
    def _initialize_firestore(self):
        """Firestoreクライアントを初期化"""
        try:
            # 環境変数からサービスアカウントキーのパスまたはJSONを取得
            service_account_path = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
            service_account_json = os.environ.get('FIREBASE_SERVICE_ACCOUNT_JSON')
            project_id = os.environ.get('FIREBASE_PROJECT_ID')
            
            if service_account_json:
                # JSON文字列から認証情報を作成
                service_account_info = json.loads(service_account_json)
                cred = credentials.Certificate(service_account_info)
                project_id = service_account_info.get('project_id', project_id)
            elif service_account_path and os.path.exists(service_account_path):
                # ファイルパスから認証情報を作成
                cred = credentials.Certificate(service_account_path)
            else:
                logger.warning("Firebase認証情報が見つかりません。ローカルストレージを使用します。")
                return
            
            # Firebase Admin SDKを初期化
            if not firebase_admin._apps:
                self.app = firebase_admin.initialize_app(cred, {
                    'projectId': project_id
                })
            else:
                self.app = firebase_admin.get_app()
            
            # Firestoreクライアントを取得
            self.db = firestore.Client(project=project_id)
            self.is_initialized = True
            logger.info(f"Firestore初期化成功: プロジェクト {project_id}")
            
        except Exception as e:
            logger.error(f"Firestore初期化失敗: {str(e)}")
            self.is_initialized = False
    
    def is_available(self) -> bool:
        """Firestoreが利用可能かチェック"""
        return self.is_initialized and self.db is not None
    
    def create_document(self, collection: str, document_id: Optional[str] = None, data: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """ドキュメントを作成"""
        if not self.is_available() or self.db is None:
            logger.warning("Firestoreが利用できません")
            return None
        
        try:
            collection_ref = self.db.collection(collection)
            
            if document_id:
                doc_ref = collection_ref.document(document_id)
                doc_ref.set(data or {})
                logger.info(f"ドキュメント作成: {collection}/{document_id}")
                return document_id
            else:
                doc_ref = collection_ref.add(data or {})
                doc_id = doc_ref[1].id
                logger.info(f"ドキュメント作成: {collection}/{doc_id}")
                return doc_id
                
        except Exception as e:
            logger.error(f"ドキュメント作成失敗: {str(e)}")
            return None
    
    def get_document(self, collection: str, document_id: str) -> Optional[Dict[str, Any]]:
        """ドキュメントを取得"""
        if not self.is_available() or self.db is None:
            logger.warning("Firestoreが利用できません")
            return None
        
        try:
            doc_ref = self.db.collection(collection).document(document_id)
            doc = doc_ref.get()
            
            if doc.exists:
                data = doc.to_dict()
                logger.info(f"ドキュメント取得: {collection}/{document_id}")
                return data
            else:
                logger.info(f"ドキュメントが存在しません: {collection}/{document_id}")
                return None
                
        except Exception as e:
            logger.error(f"ドキュメント取得失敗: {str(e)}")
            return None
    
    def update_document(self, collection: str, document_id: str, data: Dict[str, Any]) -> bool:
        """ドキュメントを更新"""
        if not self.is_available() or self.db is None:
            logger.warning("Firestoreが利用できません")
            return False
        
        try:
            doc_ref = self.db.collection(collection).document(document_id)
            doc_ref.update(data)
            logger.info(f"ドキュメント更新: {collection}/{document_id}")
            return True
            
        except Exception as e:
            logger.error(f"ドキュメント更新失敗: {str(e)}")
            return False
    
    def delete_document(self, collection: str, document_id: str) -> bool:
        """ドキュメントを削除"""
        if not self.is_available() or self.db is None:
            logger.warning("Firestoreが利用できません")
            return False
        
        try:
            doc_ref = self.db.collection(collection).document(document_id)
            doc_ref.delete()
            logger.info(f"ドキュメント削除: {collection}/{document_id}")
            return True
            
        except Exception as e:
            logger.error(f"ドキュメント削除失敗: {str(e)}")
            return False
    
    def get_collection(self, collection: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """コレクション内の全ドキュメントを取得"""
        if not self.is_available() or self.db is None:
            logger.warning("Firestoreが利用できません")
            return []
        
        try:
            collection_ref = self.db.collection(collection)
            
            if limit:
                docs = collection_ref.limit(limit).stream()
            else:
                docs = collection_ref.stream()
            
            results = []
            for doc in docs:
                data = doc.to_dict()
                if data:
                    data['_id'] = doc.id  # ドキュメントIDを含める
                    results.append(data)
            
            logger.info(f"コレクション取得: {collection} ({len(results)}件)")
            return results
            
        except Exception as e:
            logger.error(f"コレクション取得失敗: {str(e)}")
            return []
    
    def query_documents(self, collection: str, field: str, operator: str, value: Any, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """条件付きクエリでドキュメントを検索"""
        if not self.is_available() or self.db is None:
            logger.warning("Firestoreが利用できません")
            return []
        
        try:
            collection_ref = self.db.collection(collection)
            query = collection_ref.where(field, operator, value)
            
            if limit:
                query = query.limit(limit)
            
            docs = query.stream()
            results = []
            for doc in docs:
                data = doc.to_dict()
                if data:
                    data['_id'] = doc.id
                    results.append(data)
            
            logger.info(f"クエリ実行: {collection} where {field} {operator} {value} ({len(results)}件)")
            return results
            
        except Exception as e:
            logger.error(f"クエリ実行失敗: {str(e)}")
            return []

# グローバルインスタンス
firestore_manager = FirestoreManager() 