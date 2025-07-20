import pytest
import requests
import time
import os
import base64
import glob
from uuid import uuid4

BASE_URL = "http://127.0.0.1:5000"
WORKSPACE_URL = f"{BASE_URL}/user/workspaces"
EXISTING_USER_EMAIL = "testAccount@gmail.com"
EXISTING_USER_PASSWORD = "zxcv7898"

def get_jwt():
    """獲取 JWT token"""
    try:
        response = requests.post(f"{BASE_URL}/user/login", json={
            "email": EXISTING_USER_EMAIL,
            "password": EXISTING_USER_PASSWORD
        })
        print(f"登入回應: {response.status_code} - {response.text}")
        if response.status_code == 200:
            return response.json().get('jwt')
        else:
            print(f"登入失敗: {response.json()}")
            return None
    except requests.exceptions.ConnectionError as e:
        print(f"連線錯誤: {e}")
        print("請確認伺服器是否在 http://127.0.0.1:5000 運行")
        return None

def ensure_workspace_bound_to_user(workspace_id, user_id=None):
    """確保工作區綁定到指定用戶上"""
    jwt = get_jwt()
    if not jwt:
        print("無法獲取 JWT token，無法綁定工作區")
        return False
        
    headers = {"Authorization": f"Bearer {jwt}"}
    
    if not user_id:
        login_response = requests.post(f"{BASE_URL}/user/login", json={
            "email": EXISTING_USER_EMAIL,
            "password": EXISTING_USER_PASSWORD
        })
        
        if login_response.status_code != 200:
            print("無法登入獲取用戶ID")
            return False
            
        response_data = login_response.json()
        if 'user_id' in response_data:
            user_id = response_data['user_id']
        elif 'user' in response_data and 'user_id' in response_data['user']:
            user_id = response_data['user']['user_id']
        else:
            print("無法從登入響應中獲取用戶ID")
            print(f"登入響應: {response_data}")
            return False
    
    bind_response = requests.get(
        f"{BASE_URL}/user/{user_id}/workspace/{workspace_id}",
        headers=headers
    )
    
    print(f"綁定工作區回應: {bind_response.status_code} - {bind_response.text}")
    return bind_response.status_code == 200

def create_test_workspace():
    """創建一個測試用的工作區"""
    jwt = get_jwt()
    if not jwt:
        print("無法獲取 JWT token")
        return None
        
    headers = {"Authorization": f"Bearer {jwt}"}
    
    # 創建工作區，使用唯一名稱避免衝突
    workspace_name = f"test_workspace_{uuid4().hex[:8]}"
    workspace_response = requests.post(WORKSPACE_URL, 
                                     headers=headers,
                                     json={"name": workspace_name})
    
    print(f"創建工作區回應: {workspace_response.status_code} - {workspace_response.text}")
    
    if workspace_response.status_code not in [200, 201]:
        print(f"創建工作區失敗: {workspace_response.status_code}")
        return None
        
    workspace_data = workspace_response.json()
    workspace_id = workspace_data.get('workspace', {}).get('workspace_id') or workspace_data.get('workspace_id')
    
    if not workspace_id:
        print("無法從回應中獲取工作區ID")
        return None
        
    print(f"已創建工作區: {workspace_id}")
    
    # 確保工作區綁定到用戶
    if not ensure_workspace_bound_to_user(workspace_id):
        print("警告: 無法將工作區綁定到用戶")
        return None
        
    return workspace_id

def test_create_workspace_flow():
    """測試創建工作區的完整流程"""
    # 1. 創建工作區
    workspace_id = create_test_workspace()
    assert workspace_id is not None, "無法創建工作區"
    
    # 2. 驗證工作區狀態
    jwt = get_jwt()
    assert jwt is not None, "無法獲取 JWT token"
    headers = {"Authorization": f"Bearer {jwt}"}
    
    response = requests.get(f"{WORKSPACE_URL}/{workspace_id}", headers=headers)
    assert response.status_code == 200, "無法獲取工作區資訊"
    
    workspace_info = response.json()
    print(f"工作區資訊: {workspace_info}")
    
    # 3. 清理：刪除工作區（可選）
    # delete_response = requests.delete(f"{WORKSPACE_URL}/{workspace_id}", headers=headers)
    # assert delete_response.status_code == 200, "無法刪除工作區"
    
    print(f"測試完成，工作區 ID: {workspace_id}")
    return workspace_id

if __name__ == "__main__":
    print("=== 開始工作區管理測試 ===")
    workspace_id = test_create_workspace_flow()
    if workspace_id:
        print(f"成功創建工作區，ID: {workspace_id}")
    else:
        print("工作區創建失敗")
        exit(1)
