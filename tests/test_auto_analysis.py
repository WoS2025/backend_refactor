import pytest
import requests
import time
import base64

BASE_URL = "http://127.0.0.1:5000"
WORKSPACE_URL = f"{BASE_URL}/user/workspaces"
EXISTING_USER_EMAIL = "a12345@gmail.com"
EXISTING_USER_PASSWORD = "Allen9384"

def get_jwt():
    """獲取 JWT token"""
    try:
        response = requests.post(f"{BASE_URL}/user/login", json={
            "email": EXISTING_USER_EMAIL,
            "password": EXISTING_USER_PASSWORD
        })
        print(f"Login response: {response.status_code} - {response.text}")
        if response.status_code == 200:
            return response.json().get('jwt')  # 修正字段名從 'token' 到 'jwt'
        else:
            print(f"Login failed: {response.json()}")
            return None
    except requests.exceptions.ConnectionError as e:
        print(f"Connection error: {e}")
        print("請確認伺服器是否在 http://127.0.0.1:5000 運行")
        return None

def test_file_upload_triggers_analysis():
    """測試文件上傳後自動觸發分析"""
    jwt = get_jwt()
    if not jwt:
        print("無法獲取 JWT token，跳過測試")
        return
        
    print(f"JWT token: {jwt}")
    headers = {"Authorization": f"Bearer {jwt}"}
    
    # 1. 創建工作區
    workspace_response = requests.post(WORKSPACE_URL, 
                                     headers=headers,
                                     json={"name": "test_auto_analysis"})
    print(f"Workspace creation response: {workspace_response.status_code} - {workspace_response.text}")
    
    if workspace_response.status_code not in [200, 201]:
        print(f"Workspace creation failed. Status: {workspace_response.status_code}")
        print(f"Response text: {workspace_response.text}")
        try:
            print(f"Response JSON: {workspace_response.json()}")
        except:
            pass
        return
        
    # 從 workspace 物件中獲取 workspace_id
    workspace_data = workspace_response.json()
    workspace_id = workspace_data.get('workspace', {}).get('workspace_id') or workspace_data.get('workspace_id')
    print(f"Created workspace ID: {workspace_id}")
    print(f"Created workspace ID: {workspace_id}")
    
    # 2. 上傳測試文件
    test_file_content = """
    Title: Test Paper on Machine Learning
    Author: John Doe, Jane Smith
    Year: 2023
    Field: Computer Science
    Institution: Test University
    Country: USA
    Keywords: machine learning, artificial intelligence, deep learning
    References: 15
    Abstract: This paper discusses the latest advances in machine learning...
    """
    
    encoded_content = base64.b64encode(test_file_content.encode()).decode()
    
    file_response = requests.put(f"{WORKSPACE_URL}/{workspace_id}/files",
                               headers=headers,
                               json={
                                   "file": [{
                                       "name": "test_paper.txt",
                                       "content": encoded_content
                                   }]
                               })
    print(f"File upload response: {file_response.status_code} - {file_response.text}")
    
    if file_response.status_code != 200:
        print(f"File upload failed: {file_response.json()}")
        return
        
    # 3. 等待分析完成（給一些時間讓分析執行）
    time.sleep(3)
    
    # 4. 檢查分析結果
    analysis_response = requests.get(f"{WORKSPACE_URL}/{workspace_id}/analysis/all",
                                   headers=headers)
    print(f"Analysis all response: {analysis_response.status_code} - {analysis_response.text}")
    
    if analysis_response.status_code == 200:
        analysis_results = analysis_response.json()
        print(f"Analysis results: {analysis_results}")
        print(f"Found {len(analysis_results)} analysis results")
    
    # 5. 檢查特定分析類型
    analysis_types = [
        'keyword_occurence',
        'author_year', 
        'reference',
        'field_occurence',
        'field_year',
        'institution',
        'institution_year',
        'country_year'
    ]
    
    for analysis_type in analysis_types:
        type_response = requests.get(f"{WORKSPACE_URL}/{workspace_id}/analysis/type/{analysis_type}",
                                   headers=headers)
        print(f"Analysis type {analysis_type}: {type_response.status_code}")
    
    # 6. 清理：刪除測試工作區
    delete_response = requests.delete(f"{WORKSPACE_URL}/{workspace_id}",
                                    headers=headers)
    print(f"Delete response: {delete_response.status_code}")

def test_get_existing_workspaces():
    """獲取現有工作區列表"""
    jwt = get_jwt()
    if not jwt:
        print("無法獲取 JWT token，跳過測試")
        return
        
    headers = {"Authorization": f"Bearer {jwt}"}
    
    # 獲取所有工作區
    response = requests.get(WORKSPACE_URL, headers=headers)
    print(f"Get workspaces response: {response.status_code} - {response.text}")
    
    if response.status_code == 200:
        workspaces = response.json()
        print(f"Found {len(workspaces)} workspaces:")
        for workspace in workspaces:
            print(f"  - ID: {workspace.get('workspace_id')}, Name: {workspace.get('name')}")
        return workspaces
    return []

def test_manual_analysis_trigger():
    """測試手動觸發所有分析"""
    jwt = get_jwt()
    if not jwt:
        print("無法獲取 JWT token，跳過測試")
        return
        
    headers = {"Authorization": f"Bearer {jwt}"}
    
    # 先獲取現有工作區
    workspaces = test_get_existing_workspaces()
    if not workspaces:
        print("沒有找到現有工作區")
        return
        
    existing_workspace_id = workspaces[0].get('workspace_id')
    print(f"Using workspace ID: {existing_workspace_id}")
    
    # 手動觸發所有分析
    trigger_response = requests.post(f"{WORKSPACE_URL}/{existing_workspace_id}/analysis/run-all",
                                   headers=headers)
    print(f"Manual trigger response: {trigger_response.status_code} - {trigger_response.text}")
    
    # 檢查分析結果
    time.sleep(2)
    analysis_response = requests.get(f"{WORKSPACE_URL}/{existing_workspace_id}/analysis/all",
                                   headers=headers)
    print(f"Analysis results after manual trigger: {analysis_response.status_code}")

def test_get_analysis_by_type():
    """測試根據類型獲取分析結果"""
    jwt = get_jwt()
    if not jwt:
        print("無法獲取 JWT token，跳過測試")
        return
        
    headers = {"Authorization": f"Bearer {jwt}"}
    
    # 先獲取現有工作區
    workspaces = test_get_existing_workspaces()
    if not workspaces:
        print("沒有找到現有工作區")
        return
        
    existing_workspace_id = workspaces[0].get('workspace_id')
    print(f"Testing analysis types for workspace: {existing_workspace_id}")
    
    analysis_types = [
        'keyword_occurence',
        'author_year',
        'reference',
        'field_occurence',
        'field_year',
        'institution',
        'institution_year',
        'country_year'
    ]
    
    for analysis_type in analysis_types:
        response = requests.get(f"{WORKSPACE_URL}/{existing_workspace_id}/analysis/type/{analysis_type}",
                              headers=headers)
        print(f"Analysis type {analysis_type}: {response.status_code}")
        if response.status_code == 200:
            print(f"  Result: {response.json()}")

def test_get_workspace_by_id(workspace_id):
    """直接用 workspace_id 測試查詢 API"""
    jwt = get_jwt()
    if not jwt:
        print("無法獲取 JWT token，跳過測試")
        return
    headers = {"Authorization": f"Bearer {jwt}"}
    url = f"{WORKSPACE_URL}/{workspace_id}"
    response = requests.get(url, headers=headers)
    print(f"Get workspace by id response: {response.status_code} - {response.text}")
    if response.status_code == 200:
        print(f"Workspace found: {response.json()}")
    else:
        print(f"Workspace not found or無權限。請檢查 user_id 與 workspace_id 關聯。")

if __name__ == "__main__":
    # 先獲取現有工作區信息
    print("=== 獲取現有工作區 ===")
    test_get_existing_workspaces()
    
    # 運行測試
    print("\n=== 測試文件上傳觸發分析 ===")
    test_file_upload_triggers_analysis()
    
    print("\n=== 測試手動觸發分析 ===")
    test_manual_analysis_trigger()
    
    print("\n=== 測試按類型獲取分析結果 ===")
    test_get_analysis_by_type()
    
    print("\n=== 直接用指定 workspace_id 測試查詢 ===")
    test_get_workspace_by_id("200270e4-2982-409f-8424-e3817969ca80")
    
    print("\n=== 所有測試完成 ===")
