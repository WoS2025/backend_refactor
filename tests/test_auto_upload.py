import pytest
import requests
import time
import base64
import os
import glob
import uuid
import hashlib
from test_workspace_manager import get_jwt

# 全域設定
TEST_EMAIL = "testAccount@gmail.com"
TEST_PASSWORD = "zxcv7898"
MAX_FILES_PER_WORKSPACE = 2

# API 基本設定
BASE_URL = "http://127.0.0.1:5000"
WORKSPACE_URL = f"{BASE_URL}/user/workspaces"

# 資料夾路徑設定
LLM_DATA_FOLDER = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "llm")
FEDERATED_DATA_FOLDER = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "Federated")

def register_test_user():
    """註冊測試帳號"""
    register_data = {
        "username": "testUser",  # 修改：使用 username 而不是 name
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    }
    
    try:
        response = requests.post(f"{BASE_URL}/user/register", json=register_data)
        response_data = response.json()
        
        if response.status_code == 200:
            print(f"✓ 測試帳號註冊成功: {TEST_EMAIL}")
            return True
        elif response.status_code == 400 and "already registered" in response_data.get("message", ""):
            print(f"✓ 測試帳號已存在: {TEST_EMAIL}")
            return True
        else:
            print(f"✗ 註冊失敗: {response_data}")
            return False
    except Exception as e:
        print(f"✗ 註冊時出錯: {e}")
        return False

def create_test_workspace(workspace_name_prefix="auto_upload_test"):
    """創建測試工作區並綁定到用戶"""
    jwt = get_jwt()
    if not jwt:
        print("無法獲取 JWT token")
        return None
        
    headers = {"Authorization": f"Bearer {jwt}"}
    
    # 生成唯一後綴（使用時間戳和隨機字符）
    unique_suffix = hashlib.md5(f"{time.time()}{uuid.uuid4()}".encode()).hexdigest()[:8]
    workspace_name = f"{workspace_name_prefix}_{unique_suffix}"
    
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
        
        if workspace_id:
            # 綁定工作區到用戶
            if bind_workspace_to_user(workspace_id):
                print(f"✓ 創建工作區成功並已綁定到用戶: {workspace_name} (ID: {workspace_id})")
                return workspace_id
            else:
                print(f"! 工作區創建成功但綁定失敗: {workspace_name} (ID: {workspace_id})")
                return workspace_id  # 仍然返回workspace_id，讓測試繼續
        else:
            print("✗ 無法從回應中獲取工作區ID")
            return None
    else:
        print(f"✗ 創建工作區失敗: {response.text}")
        return None

def bind_workspace_to_user(workspace_id):
    """綁定工作區到用戶"""
    jwt = get_jwt()
    if not jwt:
        print("無法獲取 JWT token，無法綁定工作區")
        return False
        
    headers = {"Authorization": f"Bearer {jwt}"}
    
    # 獲取用戶ID
    try:
        user_response = requests.get(f"{BASE_URL}/user/email/{TEST_EMAIL}", headers=headers)
        if user_response.status_code == 200:
            user_data = user_response.json()
            user_id = user_data.get('user', {}).get('user_id')
            if not user_id:
                print("無法獲取用戶ID")
                return False
        else:
            print(f"獲取用戶資訊失敗: {user_response.text}")
            return False
    except Exception as e:
        print(f"獲取用戶資訊時出錯: {e}")
        return False
    
    # 綁定工作區到用戶
    try:
        bind_response = requests.get(
            f"{BASE_URL}/user/{user_id}/workspace/{workspace_id}",
            headers=headers
        )
        
        print(f"綁定工作區回應: {bind_response.status_code} - {bind_response.text}")
        return bind_response.status_code == 200
    except Exception as e:
        print(f"綁定工作區時出錯: {e}")
        return False

def test_llm_batch_analysis():
    """測試 LLM 資料夾的批次分析 - 每個工作區最多2個檔案，使用規範化命名"""
    
    print("\n=== 開始 LLM 批次分析測試 ===")
    
    # 1. 確保測試帳號已註冊
    if not register_test_user():
        pytest.fail("無法註冊或確認測試帳號")
    
    # 2. 獲取 JWT token
    jwt = get_jwt()
    if not jwt:
        pytest.fail("無法獲取 JWT token")
    
    headers = {"Authorization": f"Bearer {jwt}"}
    
    # 3. 獲取所有 LLM 資料夾中的 .txt 文件並按順序排列
    txt_files = glob.glob(os.path.join(LLM_DATA_FOLDER, "*.txt"))
    if not txt_files:
        pytest.fail(f"在 {LLM_DATA_FOLDER} 中找不到 .txt 文件")
    
    # 按照文件名順序排列
    txt_files.sort()
    print(f"找到 {len(txt_files)} 個 LLM 文件，按順序處理")
    
    # 4. 按照每個工作區最多2個檔案進行分組
    file_batches = []
    for i in range(0, len(txt_files), MAX_FILES_PER_WORKSPACE):
        batch = txt_files[i:i + MAX_FILES_PER_WORKSPACE]
        file_batches.append(batch)
    
    print(f"將文件分為 {len(file_batches)} 個批次進行處理")
    
    successful_analyses = 0
    failed_analyses = 0
    total_workspaces = len(file_batches)
    
    # 5. 處理每個批次
    for batch_index, file_batch in enumerate(file_batches):
        batch_number = batch_index + 1
        print(f"\n--- 處理 LLM 批次 {batch_number}/{total_workspaces} ---")
        print(f"此批次包含 {len(file_batch)} 個文件（按順序）:")
        for i, file_path in enumerate(file_batch):
            print(f"  [{i+1}] {os.path.basename(file_path)}")
        
        try:
            # 創建工作區，使用規範化命名：LLM_Batch_N_xxxxxxxx
            workspace_id = create_test_workspace(f"LLM_Batch_{batch_number}")
            if not workspace_id:
                print(f"批次 {batch_number}: ✗ 創建工作區失敗")
                failed_analyses += 1
                continue
            
            # 準備文件內容（按照順序處理）
            batch_files_to_upload = []
            for file_path in file_batch:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        file_content = f.read()
                    
                    encoded_content = base64.b64encode(file_content.encode()).decode()
                    file_name = os.path.basename(file_path)
                    
                    batch_files_to_upload.append({
                        "name": file_name,
                        "content": encoded_content
                    })
                    
                    print(f"  ✓ 處理完成: {file_name} ({len(file_content)} 字符)")
                    
                except Exception as e:
                    print(f"  ✗ 讀取文件失敗: {file_path}, 錯誤: {e}")
                    continue
            
            if not batch_files_to_upload:
                print(f"批次 {batch_number}: 沒有可用的文件")
                failed_analyses += 1
                continue
            
            # 上傳文件
            try:
                file_response = requests.put(
                    f"{WORKSPACE_URL}/{workspace_id}/files",
                    headers=headers,
                    json={"file": batch_files_to_upload}
                )
                
                if file_response.status_code == 200:
                    print(f"批次 {batch_number}: ✓ 上傳成功 - {len(batch_files_to_upload)} 個文件")
                else:
                    print(f"批次 {batch_number}: ✗ 上傳失敗 - {file_response.text}")
                    failed_analyses += 1
                    continue
                    
            except Exception as e:
                print(f"批次 {batch_number}: ✗ 上傳時發生錯誤 - {e}")
                failed_analyses += 1
                continue
            
            # 等待分析完成
            if wait_for_analysis_completion(workspace_id, headers, max_wait_time=90):
                if verify_analysis_results(workspace_id, headers):
                    successful_analyses += 1
                    print(f"批次 {batch_number}: ✓ 分析完成並驗證成功")
                else:
                    failed_analyses += 1
                    print(f"批次 {batch_number}: ✗ 分析驗證失敗")
            else:
                failed_analyses += 1
                print(f"批次 {batch_number}: ✗ 分析超時")
                
        except Exception as e:
            failed_analyses += 1
            print(f"批次 {batch_number}: ✗ 處理失敗 - {e}")
    
    # 6. 總結報告
    print(f"\n=== LLM 批次分析總結 ===")
    print(f"總計處理文件: {len(txt_files)} 個")
    print(f"創建工作區: {total_workspaces} 個")
    print(f"每工作區文件限制: {MAX_FILES_PER_WORKSPACE} 個")
    print(f"成功分析: {successful_analyses} 個工作區")
    print(f"失敗分析: {failed_analyses} 個工作區")
    print(f"成功率: {successful_analyses / total_workspaces * 100:.1f}%" if total_workspaces > 0 else "N/A")
    
    # 基本驗證
    assert successful_analyses > 0, "應該至少有一個成功的分析"
    success_rate = successful_analyses / total_workspaces if total_workspaces > 0 else 0
    assert success_rate >= 0.7, f"成功率過低: {success_rate:.1%}"

def test_federated_batch_analysis():
    """測試 Federated 資料夾的批次分析 - 每個工作區最多2個檔案，使用規範化命名"""
    
    print("\n=== 開始 Federated 批次分析測試 ===")
    
    # 1. 確保測試帳號已註冊
    if not register_test_user():
        pytest.fail("無法註冊或確認測試帳號")
    
    # 2. 獲取 JWT token
    jwt = get_jwt()
    if not jwt:
        pytest.fail("無法獲取 JWT token")
    
    headers = {"Authorization": f"Bearer {jwt}"}
    
    # 3. 獲取所有 Federated 資料夾中的 .txt 文件並按順序排列
    txt_files = glob.glob(os.path.join(FEDERATED_DATA_FOLDER, "*.txt"))
    if not txt_files:
        pytest.fail(f"在 {FEDERATED_DATA_FOLDER} 中找不到 .txt 文件")
    
    # 按照文件名順序排列
    txt_files.sort()
    print(f"找到 {len(txt_files)} 個 Federated 文件，按順序處理")
    
    # 4. 按照每個工作區最多2個檔案進行分組
    file_batches = []
    for i in range(0, len(txt_files), MAX_FILES_PER_WORKSPACE):
        batch = txt_files[i:i + MAX_FILES_PER_WORKSPACE]
        file_batches.append(batch)
    
    print(f"將文件分為 {len(file_batches)} 個批次進行處理")
    
    successful_analyses = 0
    failed_analyses = 0
    total_workspaces = len(file_batches)
    
    # 5. 處理每個批次
    for batch_index, file_batch in enumerate(file_batches):
        batch_number = batch_index + 1
        print(f"\n--- 處理 Federated 批次 {batch_number}/{total_workspaces} ---")
        print(f"此批次包含 {len(file_batch)} 個文件（按順序）:")
        for i, file_path in enumerate(file_batch):
            print(f"  [{i+1}] {os.path.basename(file_path)}")
        
        try:
            # 創建工作區，使用規範化命名：Federated_Batch_N_xxxxxxxx
            workspace_id = create_test_workspace(f"Federated_Batch_{batch_number}")
            if not workspace_id:
                print(f"批次 {batch_number}: ✗ 創建工作區失敗")
                failed_analyses += 1
                continue
            
            # 準備文件內容（按照順序處理）
            batch_files_to_upload = []
            for file_path in file_batch:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        file_content = f.read()
                    
                    encoded_content = base64.b64encode(file_content.encode()).decode()
                    file_name = os.path.basename(file_path)
                    
                    batch_files_to_upload.append({
                        "name": file_name,
                        "content": encoded_content
                    })
                    
                    print(f"  ✓ 處理完成: {file_name} ({len(file_content)} 字符)")
                    
                except Exception as e:
                    print(f"  ✗ 讀取文件失敗: {file_path}, 錯誤: {e}")
                    continue
            
            if not batch_files_to_upload:
                print(f"批次 {batch_number}: 沒有可用的文件")
                failed_analyses += 1
                continue
            
            # 上傳文件
            try:
                file_response = requests.put(
                    f"{WORKSPACE_URL}/{workspace_id}/files",
                    headers=headers,
                    json={"file": batch_files_to_upload}
                )
                
                if file_response.status_code == 200:
                    print(f"批次 {batch_number}: ✓ 上傳成功 - {len(batch_files_to_upload)} 個文件")
                else:
                    print(f"批次 {batch_number}: ✗ 上傳失敗 - {file_response.text}")
                    failed_analyses += 1
                    continue
                    
            except Exception as e:
                print(f"批次 {batch_number}: ✗ 上傳時發生錯誤 - {e}")
                failed_analyses += 1
                continue
            
            # 等待分析完成
            if wait_for_analysis_completion(workspace_id, headers, max_wait_time=90):
                if verify_analysis_results(workspace_id, headers):
                    successful_analyses += 1
                    print(f"批次 {batch_number}: ✓ 分析完成並驗證成功")
                else:
                    failed_analyses += 1
                    print(f"批次 {batch_number}: ✗ 分析驗證失敗")
            else:
                failed_analyses += 1
                print(f"批次 {batch_number}: ✗ 分析超時")
                
        except Exception as e:
            failed_analyses += 1
            print(f"批次 {batch_number}: ✗ 處理失敗 - {e}")
    
    # 6. 總結報告
    print(f"\n=== Federated 批次分析總結 ===")
    print(f"總計處理文件: {len(txt_files)} 個")
    print(f"創建工作區: {total_workspaces} 個")
    print(f"每工作區文件限制: {MAX_FILES_PER_WORKSPACE} 個")
    print(f"成功分析: {successful_analyses} 個工作區")
    print(f"失敗分析: {failed_analyses} 個工作區")
    print(f"成功率: {successful_analyses / total_workspaces * 100:.1f}%" if total_workspaces > 0 else "N/A")
    
    # 基本驗證
    assert successful_analyses > 0, "應該至少有一個成功的分析"
    success_rate = successful_analyses / total_workspaces if total_workspaces > 0 else 0
    assert success_rate >= 0.7, f"成功率過低: {success_rate:.1%}"

def wait_for_analysis_completion(workspace_id, headers, max_wait_time=60):
    """等待分析完成"""
    wait_interval = 5
    
    for wait_count in range(max_wait_time // wait_interval):
        print(f"  等待分析完成... {wait_count * wait_interval} 秒")
        time.sleep(wait_interval)
        
        try:
            response = requests.get(f"{WORKSPACE_URL}/{workspace_id}/analysis/all", headers=headers)
            
            if response.status_code == 200:
                results = response.json()
                if isinstance(results, dict) and any(results.values()):
                    print("  分析完成！")
                    return True
                    
        except Exception as e:
            print(f"  檢查分析狀態時出錯: {e}")
    
    print("  等待超時，分析可能尚未完成")
    return False

def verify_analysis_results(workspace_id, headers):
    """驗證分析結果"""
    try:
        response = requests.get(f"{WORKSPACE_URL}/{workspace_id}/analysis/all", headers=headers)
        
        if response.status_code == 200:
            results = response.json()
            if isinstance(results, dict):
                print(f"  分析結果類型數量: {len(results)}")
                for analysis_type, type_results in results.items():
                    result_info = len(type_results) if isinstance(type_results, list) else 'dict'
                    print(f"  - {analysis_type}: {result_info}")
                
                # 基本驗證：至少要有一些分析結果
                return len(results) > 0
            else:
                print("  分析結果格式不正確")
                return False
        else:
            print(f"  獲取分析結果失敗: {response.text}")
            return False
            
    except Exception as e:
        print(f"  驗證分析結果時出錯: {e}")
        return False
    
if __name__ == "__main__":
    print("=== 開始 LLM 批次分析測試 ===")
    test_llm_batch_analysis()
    print("\n=== 開始 Federated 批次分析測試 ===")
    test_federated_batch_analysis()
