import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, date
import os

logger = logging.getLogger(__name__)

class FirestoreAttendanceManager:
    """Firestore ベースの勤怠データ管理クラス"""
    
    def __init__(self):
        # Firestoreマネージャーをインポート
        from firestore_config import firestore_manager
        self.firestore = firestore_manager
        
        # コレクション名
        self.attendance_collection = 'attendance_data'
        self.user_attendance_collection = 'user_attendance'
        
        # ローカルストレージのファイルパス（フォールバック用）
        self.local_file_path = 'attendance_data.json'
        
        # メモリキャッシュ
        self.attendance_cache = {}
        
        # 初期化時にデータをロード
        self.load_attendance_cache()
    
    def load_attendance_cache(self):
        """勤怠データをキャッシュに読み込み"""
        try:
            if self.firestore.is_available():
                # Firestoreから読み込み
                self._load_from_firestore()
            else:
                # ローカルファイルから読み込み
                self._load_from_local_file()
                
        except Exception as e:
            logger.error(f"勤怠データロード失敗: {str(e)}")
            self.attendance_cache = {}
    
    def _load_from_firestore(self):
        """Firestoreから勤怠データを読み込み"""
        try:
            # ユーザー別勤怠データを取得
            user_attendance_docs = self.firestore.get_collection(self.user_attendance_collection)
            
            self.attendance_cache = {}
            
            for doc in user_attendance_docs:
                username = doc.get('username')
                attendance_data = doc.get('attendance_data', {})
                
                if username:
                    self.attendance_cache[username] = attendance_data
            
            logger.info(f"Firestoreから勤怠データロード完了: {len(self.attendance_cache)}ユーザー")
            
        except Exception as e:
            logger.error(f"Firestore勤怠データロード失敗: {str(e)}")
            # フォールバックとしてローカルファイルから読み込み
            self._load_from_local_file()
    
    def _load_from_local_file(self):
        """ローカルファイルから勤怠データを読み込み"""
        try:
            if os.path.exists(self.local_file_path):
                with open(self.local_file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.attendance_cache = data
                logger.info(f"ローカルファイルから勤怠データロード完了: {len(self.attendance_cache)}ユーザー")
            else:
                self.attendance_cache = {}
                logger.info("ローカルファイルが存在しません。空のキャッシュで開始")
                
        except Exception as e:
            logger.error(f"ローカルファイル読み込み失敗: {str(e)}")
            self.attendance_cache = {}
    
    def save_attendance_data(self) -> bool:
        """勤怠データを保存"""
        success = False
        
        try:
            if self.firestore.is_available():
                success = self._save_to_firestore()
            
            # ローカルファイルにも保存（バックアップ）
            self._save_to_local_file()
            
            return success
            
        except Exception as e:
            logger.error(f"勤怠データ保存失敗: {str(e)}")
            return False
    
    def _save_to_firestore(self) -> bool:
        """Firestoreに勤怠データを保存"""
        try:
            success_count = 0
            
            for username, attendance_data in self.attendance_cache.items():
                user_doc_data = {
                    'username': username,
                    'attendance_data': attendance_data,
                    'last_updated': datetime.now().isoformat()
                }
                
                # ユーザー名をドキュメントIDとして使用
                result = self.firestore.create_document(
                    self.user_attendance_collection,
                    username,
                    user_doc_data
                )
                
                if result:
                    success_count += 1
                else:
                    # 作成に失敗した場合は更新を試行
                    update_success = self.firestore.update_document(
                        self.user_attendance_collection,
                        username,
                        user_doc_data
                    )
                    if update_success:
                        success_count += 1
            
            logger.info(f"Firestore保存成功: {success_count}/{len(self.attendance_cache)}ユーザー")
            return success_count > 0
            
        except Exception as e:
            logger.error(f"Firestore保存失敗: {str(e)}")
            return False
    
    def _save_to_local_file(self):
        """ローカルファイルに勤怠データを保存"""
        try:
            with open(self.local_file_path, 'w', encoding='utf-8') as f:
                json.dump(self.attendance_cache, f, ensure_ascii=False, indent=2)
            logger.info("ローカルファイル保存成功")
            
        except Exception as e:
            logger.error(f"ローカルファイル保存失敗: {str(e)}")
    
    def update_user_attendance_data(self, username: str, date_str: str, field: str, value: str) -> bool:
        """ユーザーの勤怠データを更新"""
        try:
            # ユーザーのデータが存在しない場合は初期化
            if username not in self.attendance_cache:
                self.attendance_cache[username] = {}
            
            # 日付のデータが存在しない場合は初期化
            if date_str not in self.attendance_cache[username]:
                self.attendance_cache[username][date_str] = {}
            
            # データを更新
            self.attendance_cache[username][date_str][field] = value
            
            # Firestoreに即座に保存
            success = self._save_single_user_data(username)
            
            if success:
                logger.info(f"勤怠データ更新: {username} - {date_str} - {field} = {value}")
                # 成功時は最新データでキャッシュを更新
                self._refresh_user_cache(username)
            else:
                logger.error(f"勤怠データ更新失敗: {username} - {date_str} - {field} = {value}")
                # 失敗時はキャッシュを元に戻す
                if field in self.attendance_cache[username][date_str]:
                    del self.attendance_cache[username][date_str][field]
                    if not self.attendance_cache[username][date_str]:
                        del self.attendance_cache[username][date_str]
                    if not self.attendance_cache[username]:
                        del self.attendance_cache[username]
            
            return success
            
        except Exception as e:
            logger.error(f"勤怠データ更新失敗: {str(e)}")
            return False
    
    def _save_single_user_data(self, username: str) -> bool:
        """単一ユーザーのデータをFirestoreに保存"""
        try:
            if not self.firestore.is_available():
                logger.warning("Firestore利用不可、ローカルファイルのみ保存")
                self._save_to_local_file()
                return True
            
            attendance_data = self.attendance_cache.get(username, {})
            
            user_doc_data = {
                'username': username,
                'attendance_data': attendance_data,
                'last_updated': datetime.now().isoformat()
            }
            
            # ユーザー名をドキュメントIDとして使用
            result = self.firestore.create_document(
                self.user_attendance_collection,
                username,
                user_doc_data
            )
            
            if not result:
                # 作成に失敗した場合は更新を試行
                result = self.firestore.update_document(
                    self.user_attendance_collection,
                    username,
                    user_doc_data
                )
            
            # ローカルファイルにもバックアップ保存
            self._save_to_local_file()
            
            # 結果をboolに変換
            success = bool(result)
            
            if success:
                logger.debug(f"Firestore保存成功: {username}")
            else:
                logger.error(f"Firestore保存失敗: {username}")
            
            return success
            
        except Exception as e:
            logger.error(f"単一ユーザーデータ保存失敗: {str(e)}")
            return False
    
    def _refresh_user_cache(self, username: str):
        """特定ユーザーのキャッシュを最新データで更新"""
        try:
            if not self.firestore.is_available():
                return
            
            user_doc = self.firestore.get_document(self.user_attendance_collection, username)
            if user_doc:
                attendance_data = user_doc.get('attendance_data', {})
                self.attendance_cache[username] = attendance_data
                logger.debug(f"ユーザーキャッシュ更新: {username}")
            
        except Exception as e:
            logger.error(f"ユーザーキャッシュ更新失敗: {str(e)}")
    
    def get_user_attendance_data(self, username: str) -> Dict[str, Any]:
        """特定ユーザーの勤怠データを取得（最新データを保証）"""
        try:
            # まずFirestoreから最新データを取得
            if self.firestore.is_available():
                user_doc = self.firestore.get_document(self.user_attendance_collection, username)
                if user_doc:
                    attendance_data = user_doc.get('attendance_data', {})
                    # キャッシュも更新
                    self.attendance_cache[username] = attendance_data
                    logger.debug(f"最新データ取得: {username}")
                    return attendance_data
            
            # Firestoreが利用できない場合はキャッシュから取得
            return self.attendance_cache.get(username, {})
            
        except Exception as e:
            logger.error(f"勤怠データ取得失敗: {str(e)}")
            return self.attendance_cache.get(username, {})
    
    def get_user_monthly_data(self, username: str, year: int, month: int) -> Dict[str, Any]:
        """ユーザーの月別データを取得（最新データを保証）"""
        # 最新データを取得
        user_data = self.get_user_attendance_data(username)
        monthly_data = {}
        
        try:
            for date_str, daily_data in user_data.items():
                try:
                    date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
                    if date_obj.year == year and date_obj.month == month:
                        monthly_data[date_str] = daily_data
                except ValueError:
                    # 日付形式が不正な場合はスキップ
                    logger.warning(f"不正な日付形式: {date_str}")
                    continue
            
            logger.debug(f"月別データ取得: {username} - {year}/{month} - {len(monthly_data)}件")
            return monthly_data
            
        except Exception as e:
            logger.error(f"月別データ取得失敗: {str(e)}")
            return {}
    
    def get_all_users_data(self) -> Dict[str, Any]:
        """全ユーザーの勤怠データを取得"""
        return self.attendance_cache.copy()
    
    def migrate_from_legacy_format(self, legacy_data: Dict[str, Any]) -> bool:
        """従来形式のデータをFirestore形式に移行"""
        try:
            migrated_count = 0
            
            for date_str, daily_data in legacy_data.items():
                if isinstance(daily_data, dict):
                    for username, user_daily_data in daily_data.items():
                        if username not in self.attendance_cache:
                            self.attendance_cache[username] = {}
                        
                        self.attendance_cache[username][date_str] = user_daily_data
                        migrated_count += 1
            
            # 移行後のデータを保存
            success = self.save_attendance_data()
            
            logger.info(f"データ移行完了: {migrated_count}件")
            return success
            
        except Exception as e:
            logger.error(f"データ移行失敗: {str(e)}")
            return False
    
    def backup_to_json(self, backup_file_path: str) -> bool:
        """勤怠データをJSONファイルにバックアップ"""
        try:
            with open(backup_file_path, 'w', encoding='utf-8') as f:
                json.dump(self.attendance_cache, f, ensure_ascii=False, indent=2)
            logger.info(f"バックアップ完了: {backup_file_path}")
            return True
            
        except Exception as e:
            logger.error(f"バックアップ失敗: {str(e)}")
            return False
    
    def restore_from_json(self, backup_file_path: str) -> bool:
        """JSONファイルから勤怠データを復元"""
        try:
            with open(backup_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.attendance_cache = data
            
            # 復元後のデータを保存
            success = self.save_attendance_data()
            
            logger.info(f"復元完了: {backup_file_path}")
            return success
            
        except Exception as e:
            logger.error(f"復元失敗: {str(e)}")
            return False
    
    def is_available(self) -> bool:
        """勤怠データサービスが利用可能かチェック"""
        return True  # ローカルファイルフォールバックがあるため常に利用可能

# グローバルインスタンス
firestore_attendance_manager = FirestoreAttendanceManager() 