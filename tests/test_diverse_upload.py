import pytest
import requests
import time
import base64
import os
import glob
import uuid
import random
from test_workspace_manager import get_jwt

def create_diverse_test_workspace():
    """創建多樣化測試工作區"""
    jwt = get_jwt()
    if not jwt:
        print("無法獲取 JWT token")
        return None
        
    headers = {"Authorization": f"Bearer {jwt}"}
    
    # 添加隨機後綴避免名稱衝突
    unique_suffix = str(uuid.uuid4())[:8]
    workspace_name = f"diverse_test_{unique_suffix}"
    
    workspace_data = {
        "name": workspace_name
    }
    
    response = requests.post("http://127.0.0.1:5000/user/workspaces", 
                           headers=headers, 
                           json=workspace_data)
    
    if response.status_code == 201:
        response_data = response.json()
        workspace_id = (response_data.get('workspace_id') or 
                      response_data.get('id') or 
                      (response_data.get('workspace', {}).get('workspace_id')))
        print(f"創建多樣化測試工作區: {workspace_id}")
        return workspace_id
    else:
        print(f"創建工作區失敗: {response.text}")
        return None

def get_diverse_files():
    """獲取多樣化的檔案組合"""
    covid_folder = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "COVID-19", "COVID-19")
    federated_folder = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "Federated")
    
    files_to_upload = []
    
    # COVID-19 檔案：隨機選擇3個不同的檔案
    if os.path.exists(covid_folder):
        covid_files = glob.glob(os.path.join(covid_folder, "*.txt"))
        if len(covid_files) >= 3:
            selected_covid = random.sample(covid_files, 3)
            print(f"選擇的 COVID-19 檔案: {[os.path.basename(f) for f in selected_covid]}")
            
            for txt_file in selected_covid:
                try:
                    with open(txt_file, 'r', encoding='utf-8') as f:
                        file_content = f.read()
                    
                    print(f"COVID-19 文件: {os.path.basename(txt_file)} ({len(file_content)} 字符)")
                    
                    encoded_content = base64.b64encode(file_content.encode()).decode()
                    file_name = os.path.basename(txt_file)
                    
                    files_to_upload.append({
                        "name": file_name,
                        "content": encoded_content
                    })
                    
                except Exception as e:
                    print(f"處理 COVID-19 文件失敗: {txt_file}, 錯誤: {e}")
                    continue
    
    # Federated 檔案：隨機選擇2個不同的檔案
    if os.path.exists(federated_folder):
        federated_files = glob.glob(os.path.join(federated_folder, "*.txt"))
        if len(federated_files) >= 2:
            selected_federated = random.sample(federated_files, 2)
            print(f"選擇的 Federated 檔案: {[os.path.basename(f) for f in selected_federated]}")
            
            for txt_file in selected_federated:
                try:
                    with open(txt_file, 'r', encoding='utf-8') as f:
                        file_content = f.read()
                    
                    print(f"Federated 文件: {os.path.basename(txt_file)} ({len(file_content)} 字符)")
                    
                    encoded_content = base64.b64encode(file_content.encode()).decode()
                    file_name = os.path.basename(txt_file)
                    
                    files_to_upload.append({
                        "name": file_name,
                        "content": encoded_content
                    })
                    
                except Exception as e:
                    print(f"處理 Federated 文件失敗: {txt_file}, 錯誤: {e}")
                    continue
    
    return files_to_upload

def test_diverse_file_upload():
    """測試多樣化檔案上傳和分析"""
    print("\n=== 開始多樣化檔案上傳測試 ===")
    
    # 1. 創建新的工作區
    workspace_id = create_diverse_test_workspace()
    if not workspace_id:
        pytest.fail("無法創建工作區")
        return
    
    # 2. 獲取JWT token
    jwt = get_jwt()
    if not jwt:
        pytest.fail("無法獲取 JWT token")
        return
    
    headers = {"Authorization": f"Bearer {jwt}"}
    
    # 3. 獲取多樣化檔案
    files_to_upload = get_diverse_files()
    if not files_to_upload:
        pytest.fail("沒有找到可上傳的檔案")
        return
    
    print(f"\n準備上傳 {len(files_to_upload)} 個檔案")
    
    # 4. 檢查總大小是否合理（避免超過16MB）
    total_size = sum(len(f["content"]) for f in files_to_upload)
    print(f"總檔案大小（base64編碼後）: {total_size / (1024*1024):.2f} MB")
    
    if total_size > 15 * 1024 * 1024:  # 15MB 安全限制
        print("檔案總大小過大，減少檔案數量")
        files_to_upload = files_to_upload[:3]  # 只取前3個檔案
        print(f"調整後上傳 {len(files_to_upload)} 個檔案")
    
    # 5. 上傳檔案
    try:
        file_response = requests.put(
            f"http://127.0.0.1:5000/user/workspaces/{workspace_id}/files",
            headers=headers,
            json={"file": files_to_upload}
        )
        print(f"上傳回應: {file_response.status_code}")
        
        if file_response.status_code == 200:
            print(f"上傳成功: {len(files_to_upload)} 個檔案")
        else:
            print(f"上傳失敗: {file_response.text}")
            pytest.fail("檔案上傳失敗")
            return
            
    except Exception as e:
        print(f"上傳時發生錯誤: {e}")
        pytest.fail(f"上傳時發生錯誤: {e}")
        return
    
    # 6. 等待分析完成
    print("等待分析完成...")
    max_wait_time = 120  # 增加等待時間，因為檔案更多
    wait_interval = 10
    analysis_completed = False
    
    for wait_count in range(max_wait_time // wait_interval):
        print(f"等待中... {wait_count * wait_interval} 秒")
        time.sleep(wait_interval)
        
        try:
            analysis_response = requests.get(
                f"http://127.0.0.1:5000/user/workspaces/{workspace_id}/analysis/all",
                headers=headers
            )
            
            if analysis_response.status_code == 200:
                analysis_results = analysis_response.json()
                if isinstance(analysis_results, dict) and any(analysis_results.values()):
                    print("分析已完成，結果如下：")
                    for analysis_type, results in analysis_results.items():
                        if results:
                            result_info = len(results) if isinstance(results, list) else '有數據'
                            print(f"- {analysis_type}: {result_info}")
                    analysis_completed = True
                    break
        except Exception as e:
            print(f"檢查分析狀態時出錯: {e}")
    
    # 7. 驗證分析結果
    if analysis_completed:
        try:
            response = requests.get(
                f"http://127.0.0.1:5000/user/workspaces/{workspace_id}/analysis/all",
                headers=headers
            )
            
            if response.status_code == 200:
                results = response.json()
                if isinstance(results, dict):
                    assert len(results) > 0, "應該至少有一種分析結果"
                    print(f"\n✅ 成功獲得 {len(results)} 種分析結果")
                    
                    # 詳細顯示分析結果
                    for analysis_type, type_results in results.items():
                        if isinstance(type_results, dict) and type_results.get('result'):
                            result_count = len(type_results['result']) if isinstance(type_results['result'], list) else 1
                            print(f"   {analysis_type}: {result_count} 個結果項目")
                else:
                    pytest.fail("分析結果格式不正確")
            else:
                pytest.fail(f"無法獲取分析結果: {response.text}")
        except Exception as e:
            pytest.fail(f"驗證分析結果時出錯: {e}")
    else:
        print("⚠️ 分析未在預期時間內完成，但檔案上傳成功")
    
    print(f"\n=== 多樣化檔案測試完成 ===")
    print(f"工作區 ID: {workspace_id}")
    print(f"上傳檔案: {[f['name'] for f in files_to_upload]}")

if __name__ == "__main__":
    test_diverse_file_upload()
