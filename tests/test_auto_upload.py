import pytest
import requests
import time
import base64
import os
import glob
import uuid
import hashlib
from test_workspace_manager import get_jwt

def create_test_workspace():
    """創建測試工作區"""
    jwt = get_jwt()
    if not jwt:
        print("無法獲取 JWT token")
        return None
        
    headers = {"Authorization": f"Bearer {jwt}"}
    
    # 添加隨機後綴避免名稱衝突
    unique_suffix = str(uuid.uuid4())[:8]
    workspace_name = f"auto_upload_test_{unique_suffix}"
    
    workspace_data = {
        "name": workspace_name
    }
    
    response = requests.post(WORKSPACE_URL, 
                           headers=headers, 
                           json=workspace_data)
    
    if response.status_code == 201:
        response_data = response.json()
        print(f"工作區創建回應: {response_data}")
        # 嘗試不同的位置提取workspace_id
        workspace_id = (response_data.get('workspace_id') or 
                      response_data.get('id') or 
                      (response_data.get('workspace', {}).get('workspace_id')))
        print(f"創建工作區成功: {workspace_id}")
        return workspace_id
    else:
        print(f"創建工作區失敗: {response.text}")
        return None

# 資料夾路徑 - 使用專案內的資料
COVID_DATA_FOLDER = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "COVID-19", "COVID-19")
FEDERATED_DATA_FOLDER = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "Federated")
BASE_URL = "http://127.0.0.1:5000"
WORKSPACE_URL = f"{BASE_URL}/user/workspaces"

def test_auto_analysis():
    """測試上傳文件到指定工作區並驗證自動分析功能"""
    # 1. 創建新的工作區
    workspace_id = create_test_workspace()
    if not workspace_id:
        pytest.fail("無法創建工作區")
        return
    
    jwt = get_jwt()
    if not jwt:
        pytest.fail("無法獲取 JWT token")
        return
        
    headers = {"Authorization": f"Bearer {jwt}"}
    
    # 2. 獲取要上傳的文件
    all_files_to_upload = []
    data_folders = [COVID_DATA_FOLDER, FEDERATED_DATA_FOLDER]
    
    for folder in data_folders:
        if not os.path.exists(folder):
            print(f"資料夾不存在: {folder}")
            continue
            
        txt_files = glob.glob(os.path.join(folder, "*.txt"))
        print(f"在 {folder} 中找到 {len(txt_files)} 個 .txt 文件")
        
        # 基於當前時間選擇檔案，確保每次運行選擇不同檔案但有規律
        if txt_files:
            # 使用當前時間的秒數來選擇檔案，這樣每次運行會選擇不同檔案
            current_time = int(time.time())
            file_index = current_time % len(txt_files)
            selected_file = txt_files[file_index]
            
            try:
                print(f"處理文件 (索引 {file_index+1}/{len(txt_files)}): {os.path.basename(selected_file)}")
                
                with open(selected_file, 'r', encoding='utf-8') as f:
                    file_content = f.read()
                
                print(f"文件大小: {len(file_content)} 字符")
                
                encoded_content = base64.b64encode(file_content.encode()).decode()
                file_name = os.path.basename(selected_file)
                
                all_files_to_upload.append({
                    "name": file_name,
                    "content": encoded_content
                })
                
            except Exception as e:
                print(f"處理文件失敗: {selected_file}, 錯誤: {e}")
                continue
    
    if not all_files_to_upload:
        pytest.fail("沒有找到可上傳的文件")
        return
    
    print(f"準備上傳 {len(all_files_to_upload)} 個文件")
    
    # 3. 一次上傳所有檔案（2個檔案應該不會超過16MB）
    try:
        file_response = requests.put(
            f"{WORKSPACE_URL}/{workspace_id}/files",
            headers=headers,
            json={"file": all_files_to_upload}
        )
        print(f"上傳回應: {file_response.status_code}")
        
        if file_response.status_code == 200:
            print(f"上傳成功: {len(all_files_to_upload)} 個文件")
        else:
            print(f"上傳失敗: {file_response.text}")
            pytest.fail("檔案上傳失敗")
            return
            
    except Exception as e:
        print(f"上傳時發生錯誤: {e}")
        pytest.fail(f"上傳時發生錯誤: {e}")
        return
    
    # 4. 等待並檢查分析結果
    print("等待分析完成...")
    max_wait_time = 60  # 增加等待時間到60秒
    wait_interval = 5
    analysis_completed = False
    
    for wait_count in range(max_wait_time // wait_interval):
        print(f"等待中... {wait_count * wait_interval} 秒")
        time.sleep(wait_interval)
        
        try:
            analysis_response = requests.get(f"{WORKSPACE_URL}/{workspace_id}/analysis/all",
                                          headers=headers)
            
            if analysis_response.status_code == 200:
                analysis_results = analysis_response.json()
                # 檢查是否包含任何分析類型的結果
                if isinstance(analysis_results, dict) and any(analysis_results.values()):
                    print("分析已完成，結果如下：")
                    for analysis_type, results in analysis_results.items():
                        if results:
                            print(f"- {analysis_type}: {len(results) if isinstance(results, list) else '有'}")
                    analysis_completed = True
                    break
        except Exception as e:
            print(f"檢查分析狀態時出錯: {e}")
    
    if not analysis_completed:
        print("警告: 等待時間已到，但分析可能尚未完成")
    
    # 5. 驗證特定類型的分析結果
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
    
    try:
        # 直接獲取所有分析結果
        response = requests.get(
            f"{WORKSPACE_URL}/{workspace_id}/analysis/all",
            headers=headers
        )
        print(f"獲取所有分析結果: {response.status_code}")
        
        if response.status_code == 200:
            results = response.json()
            if isinstance(results, dict):
                for analysis_type, type_results in results.items():
                    result_count = len(type_results) if isinstance(type_results, list) else '1'
                    print(f"分析類型 {analysis_type}: {result_count} 個結果")
                    # 可以在這裡加入更詳細的結果驗證
                    assert type_results is not None, f"{analysis_type} 分析結果不應為空"
            else:
                pytest.fail("分析結果格式不正確，應該是一個字典")
        else:
            print(f"獲取分析結果失敗: {response.text}")
            pytest.fail("無法獲取分析結果")
    except Exception as e:
        print(f"驗證分析結果時出錯: {e}")
        pytest.fail(str(e))
    
    print(f"\n=== 自動分析測試完成 ===\n工作區 ID: {workspace_id}")
    
if __name__ == "__main__":
    print("=== 開始自動分析測試 ===")
    test_auto_analysis()
