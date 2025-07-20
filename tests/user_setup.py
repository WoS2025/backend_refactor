import requests
import time
import json

# API 基本設定
BASE_URL = "http://127.0.0.1:5000"

def register_and_login():
    """註冊並登入測試帳號"""
    # 帳號資訊
    email = "testAccount@gmail.com"
    username = "testUser"
    password = "zxcv7898"
    
    print("=== 開始註冊帳號 ===")
    
    # 1. 嘗試註冊帳號
    try:
        register_response = requests.post(f"{BASE_URL}/user/register", json={
            "username": username,
            "email": email,
            "password": password
        })
        
        print(f"註冊響應: {register_response.status_code}")
        print(f"響應內容: {register_response.text}")
        
        if register_response.status_code == 200:
            print("帳號註冊成功!")
        else:
            print(f"帳號可能已存在或註冊失敗: {register_response.json()}")
    except Exception as e:
        print(f"註冊請求出錯: {e}")
        print("請確認伺服器是否在 http://127.0.0.1:5000 運行")
        return None
    
    print("\n=== 開始登入帳號 ===")
    
    # 2. 嘗試登入帳號
    try:
        login_response = requests.post(f"{BASE_URL}/user/login", json={
            "email": email,
            "password": password
        })
        
        print(f"登入響應: {login_response.status_code}")
        print(f"響應內容: {login_response.text}")
        
        if login_response.status_code == 200:
            jwt_token = login_response.json().get('jwt')
            print("登入成功!")
            print(f"JWT 令牌: {jwt_token}")
            return jwt_token
        else:
            print(f"登入失敗: {login_response.json()}")
            return None
    except Exception as e:
        print(f"登入請求出錯: {e}")
        print("請確認伺服器是否在 http://127.0.0.1:5000 運行")
        return None

def test_token(jwt_token):
    """測試 JWT Token 是否有效"""
    if not jwt_token:
        print("沒有有效的 JWT Token")
        return False
    
    # 嘗試獲取工作區列表測試 token 是否有效
    try:
        workspaces_response = requests.get(f"{BASE_URL}/user/workspaces", 
                                         headers={"Authorization": f"Bearer {jwt_token}"})
        
        if workspaces_response.status_code == 200:
            print(f"JWT Token 有效! 已獲取 {len(workspaces_response.json())} 個工作區")
            return True
        else:
            print(f"JWT Token 似乎無效: {workspaces_response.status_code} - {workspaces_response.text}")
            return False
    except Exception as e:
        print(f"測試 JWT Token 時出錯: {e}")
        return False

if __name__ == "__main__":
    # 註冊並登入
    jwt_token = register_and_login()
    
    # 驗證 token
    if jwt_token:
        is_valid = test_token(jwt_token)
        if is_valid:
            print("\n=== JWT Token 已獲取並驗證成功 ===")
            print("已準備好運行 test_auto_analysis.py")
            print(f"請在 test_auto_analysis.py 中使用以下設定:")
            print("EXISTING_USER_EMAIL = \"testAccount@gmail.com\"")
            print("EXISTING_USER_PASSWORD = \"zxcv7898\"")
        else:
            print("\n=== JWT Token 無效，請檢查伺服器狀態 ===")
    else:
        print("\n=== 未能獲取 JWT Token ===")
