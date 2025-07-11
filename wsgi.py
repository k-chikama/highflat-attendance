import os
import base64
import json
import tempfile

# Vercel環境でのFirebase Service Account設定
def setup_firebase_credentials():
    """Vercel環境でFirebase認証情報を設定"""
    credentials_base64 = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS_BASE64')
    if credentials_base64:
        try:
            # Base64デコードしてJSONに変換
            credentials_json = base64.b64decode(credentials_base64).decode('utf-8')
            credentials_dict = json.loads(credentials_json)
            # 一時ファイルに保存
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                json.dump(credentials_dict, f)
                os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = f.name
            print(f"Firebase認証情報を設定しました: {f.name}")
        except Exception as e:
            print(f"Firebase認証情報の設定に失敗: {e}")

# Firestore専用
setup_firebase_credentials()
from app_firestore import app

if __name__ == "__main__":
    app.run() 