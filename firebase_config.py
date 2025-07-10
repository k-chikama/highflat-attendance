import os
import json
import requests
from typing import Dict, Any

class FirebaseDatabase:
    def __init__(self):
        # Firebase設定（環境変数から取得）
        self.firebase_url = os.environ.get('FIREBASE_URL')
        self.firebase_secret = os.environ.get('FIREBASE_SECRET')  # 認証が必要な場合
        
        if not self.firebase_url:
            print("WARNING: FIREBASE_URL not set, using local storage")
            self.use_firebase = False
        else:
            self.use_firebase = True
            if not self.firebase_url.endswith('/'):
                self.firebase_url += '/'
    
    def save_data(self, data: Dict[str, Any]) -> bool:
        """勤怠データをFirebaseに保存"""
        if not self.use_firebase:
            return False
            
        try:
            url = f"{self.firebase_url}attendance_data.json"
            headers = {'Content-Type': 'application/json'}
            
            response = requests.put(url, json=data, headers=headers)
            
            if response.status_code == 200:
                print("DEBUG: Firebase保存成功")
                return True
            else:
                print(f"ERROR: Firebase保存失敗 - {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            print(f"ERROR: Firebase保存例外 - {str(e)}")
            return False
    
    def load_data(self) -> Dict[str, Any]:
        """勤怠データをFirebaseから読み込み"""
        if not self.use_firebase:
            return {}
            
        try:
            url = f"{self.firebase_url}attendance_data.json"
            response = requests.get(url)
            
            if response.status_code == 200:
                data = response.json()
                print("DEBUG: Firebase読み込み成功")
                return data if data else {}
            else:
                print(f"ERROR: Firebase読み込み失敗 - {response.status_code}")
                return {}
                
        except Exception as e:
            print(f"ERROR: Firebase読み込み例外 - {str(e)}")
            return {}
    
    def is_available(self) -> bool:
        """Firebaseが利用可能かチェック"""
        return self.use_firebase

# グローバルインスタンス
firebase_db = FirebaseDatabase() 