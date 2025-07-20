import pytest
import requests
import time
import base64
import os
import glob
import uuid
from test_workspace_manager import get_jwt

class TestBatchAnalysis:
    """測試批次分析功能 - 每個工作區處理少量檔案以避免16MB限制"""
    
    BASE_URL = "http://127.0.0.1:5000"
    WORKSPACE_URL = f"{BASE_URL}/user/workspaces"
    USER_URL = f"{BASE_URL}/user"
    
    # 資料夾路徑 - 修正COVID-19路徑
    COVID_DATA_FOLDER = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "COVID-19", "COVID-19")
    FEDERATED_DATA_FOLDER = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "Federated")
    
    @staticmethod
    def get_jwt():
        """獲取JWT token"""
        return get_jwt()
    
    @staticmethod
    def create_test_workspace(workspace_name):
        """創建測試工作區"""
        jwt = TestBatchAnalysis.get_jwt()
        if not jwt:
            return None
            
        headers = {"Authorization": f"Bearer {jwt}"}
        
        # 添加隨機後綴避免名稱衝突
        unique_suffix = str(uuid.uuid4())[:8]
        unique_name = f"{workspace_name}_{unique_suffix}"
        
        workspace_data = {
            "name": unique_name
        }
        
        response = requests.post(TestBatchAnalysis.WORKSPACE_URL, 
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
    
    @staticmethod
    def get_files_from_folder(folder_path, max_files=2):
        """從資料夾按規律選擇指定數量的檔案"""
        if not os.path.exists(folder_path):
            print(f"資料夾不存在: {folder_path}")
            return []
            
        txt_files = glob.glob(os.path.join(folder_path, "*.txt"))
        
        # 基於時間戳選擇檔案，確保每次運行選擇不同檔案但有規律
        if txt_files:
            current_time = int(time.time())
            start_index = current_time % len(txt_files)
            
            # 循環選擇檔案，從start_index開始
            selected_files = []
            for i in range(min(max_files, len(txt_files))):
                file_index = (start_index + i) % len(txt_files)
                selected_files.append(txt_files[file_index])
            
            print(f"從 {len(txt_files)} 個檔案中選擇了 {len(selected_files)} 個，起始索引: {start_index}")
        else:
            selected_files = []
        
        files_to_upload = []
        for i, txt_file in enumerate(selected_files):
            try:
                with open(txt_file, 'r', encoding='utf-8') as f:
                    file_content = f.read()
                
                print(f"處理文件 {i+1}/{len(selected_files)}: {os.path.basename(txt_file)} ({len(file_content)} 字符)")
                
                encoded_content = base64.b64encode(file_content.encode()).decode()
                file_name = os.path.basename(txt_file)
                
                files_to_upload.append({
                    "name": file_name,
                    "content": encoded_content
                })
                
            except Exception as e:
                print(f"處理文件失敗: {txt_file}, 錯誤: {e}")
                continue
                
        return files_to_upload
    
    @staticmethod
    def upload_files_to_workspace(workspace_id, files):
        """上傳檔案到工作區"""
        jwt = TestBatchAnalysis.get_jwt()
        if not jwt:
            return False
            
        headers = {"Authorization": f"Bearer {jwt}"}
        
        try:
            response = requests.put(
                f"{TestBatchAnalysis.WORKSPACE_URL}/{workspace_id}/files",
                headers=headers,
                json={"file": files}
            )
            
            if response.status_code == 200:
                print(f"上傳成功: {len(files)} 個檔案")
                return True
            else:
                print(f"上傳失敗: {response.text}")
                return False
                
        except Exception as e:
            print(f"上傳時發生錯誤: {e}")
            return False
    
    @staticmethod
    def wait_for_analysis(workspace_id, max_wait_time=60):
        """等待分析完成"""
        jwt = TestBatchAnalysis.get_jwt()
        if not jwt:
            return False
            
        headers = {"Authorization": f"Bearer {jwt}"}
        wait_interval = 5
        
        for wait_count in range(max_wait_time // wait_interval):
            print(f"等待分析完成... {wait_count * wait_interval} 秒")
            time.sleep(wait_interval)
            
            try:
                response = requests.get(f"{TestBatchAnalysis.WORKSPACE_URL}/{workspace_id}/analysis/all",
                                      headers=headers)
                
                if response.status_code == 200:
                    results = response.json()
                    if isinstance(results, dict) and any(results.values()):
                        print("分析完成！")
                        return True
                        
            except Exception as e:
                print(f"檢查分析狀態時出錯: {e}")
        
        print("等待超時，分析可能尚未完成")
        return False
    
    @staticmethod
    def verify_analysis_results(workspace_id):
        """驗證分析結果"""
        jwt = TestBatchAnalysis.get_jwt()
        if not jwt:
            return False
            
        headers = {"Authorization": f"Bearer {jwt}"}
        
        try:
            response = requests.get(f"{TestBatchAnalysis.WORKSPACE_URL}/{workspace_id}/analysis/all",
                                  headers=headers)
            
            if response.status_code == 200:
                results = response.json()
                if isinstance(results, dict):
                    print(f"分析結果類型數量: {len(results)}")
                    for analysis_type, type_results in results.items():
                        result_info = len(type_results) if isinstance(type_results, list) else 'dict'
                        print(f"- {analysis_type}: {result_info}")
                    
                    # 基本驗證：至少要有一些分析結果
                    assert len(results) > 0, "應該至少有一種分析結果"
                    return True
                else:
                    print("分析結果格式不正確")
                    return False
            else:
                print(f"獲取分析結果失敗: {response.text}")
                return False
                
        except Exception as e:
            print(f"驗證分析結果時出錯: {e}")
            return False

    def test_covid_batch_analysis(self):
        """測試COVID-19資料批次分析"""
        print("\n=== COVID-19 批次分析測試 ===")
        
        # 1. 創建專用工作區
        workspace_id = self.create_test_workspace("COVID19_Batch_Test")
        assert workspace_id is not None, "無法創建工作區"
        
        # 2. 獲取檔案（最多2個）
        files = self.get_files_from_folder(self.COVID_DATA_FOLDER, max_files=2)
        assert len(files) > 0, f"COVID-19資料夾中沒有找到檔案: {self.COVID_DATA_FOLDER}"
        print(f"準備上傳 {len(files)} 個COVID-19檔案")
        
        # 3. 上傳檔案
        upload_success = self.upload_files_to_workspace(workspace_id, files)
        assert upload_success, "檔案上傳失敗"
        
        # 4. 等待分析
        analysis_ready = self.wait_for_analysis(workspace_id)
        assert analysis_ready, "分析超時"
        
        # 5. 驗證結果
        results_valid = self.verify_analysis_results(workspace_id)
        assert results_valid, "分析結果驗證失敗"
        
        print(f"COVID-19 批次分析測試完成 - 工作區: {workspace_id}")

    def test_federated_batch_analysis(self):
        """測試Federated資料批次分析"""
        print("\n=== Federated 批次分析測試 ===")
        
        # 1. 創建專用工作區
        workspace_id = self.create_test_workspace("Federated_Batch_Test")
        assert workspace_id is not None, "無法創建工作區"
        
        # 2. 獲取檔案（最多2個）
        files = self.get_files_from_folder(self.FEDERATED_DATA_FOLDER, max_files=2)
        assert len(files) > 0, f"Federated資料夾中沒有找到檔案: {self.FEDERATED_DATA_FOLDER}"
        print(f"準備上傳 {len(files)} 個Federated檔案")
        
        # 3. 上傳檔案
        upload_success = self.upload_files_to_workspace(workspace_id, files)
        assert upload_success, "檔案上傳失敗"
        
        # 4. 等待分析
        analysis_ready = self.wait_for_analysis(workspace_id)
        assert analysis_ready, "分析超時"
        
        # 5. 驗證結果
        results_valid = self.verify_analysis_results(workspace_id)
        assert results_valid, "分析結果驗證失敗"
        
        print(f"Federated 批次分析測試完成 - 工作區: {workspace_id}")

    def test_mixed_batch_analysis(self):
        """測試混合資料批次分析"""
        print("\n=== 混合資料批次分析測試 ===")
        
        # 1. 創建專用工作區
        workspace_id = self.create_test_workspace("Mixed_Batch_Test")
        assert workspace_id is not None, "無法創建工作區"
        
        # 2. 獲取混合檔案（每個資料夾1個，總共2個）
        covid_files = self.get_files_from_folder(self.COVID_DATA_FOLDER, max_files=1)
        federated_files = self.get_files_from_folder(self.FEDERATED_DATA_FOLDER, max_files=1)
        
        all_files = covid_files + federated_files
        assert len(all_files) > 0, "沒有找到可用的檔案"
        print(f"準備上傳 {len(all_files)} 個混合檔案 (COVID: {len(covid_files)}, Federated: {len(federated_files)})")
        
        # 3. 上傳檔案
        upload_success = self.upload_files_to_workspace(workspace_id, all_files)
        assert upload_success, "檔案上傳失敗"
        
        # 4. 等待分析
        analysis_ready = self.wait_for_analysis(workspace_id)
        assert analysis_ready, "分析超時"
        
        # 5. 驗證結果
        results_valid = self.verify_analysis_results(workspace_id)
        assert results_valid, "分析結果驗證失敗"
        
        print(f"混合資料批次分析測試完成 - 工作區: {workspace_id}")

if __name__ == "__main__":
    # 可以單獨運行特定測試
    test_instance = TestBatchAnalysis()
    
    print("=== 開始批次分析測試 ===")
    try:
        test_instance.test_covid_batch_analysis()
        test_instance.test_federated_batch_analysis()  
        test_instance.test_mixed_batch_analysis()
        print("\n=== 所有批次分析測試完成 ===")
    except Exception as e:
        print(f"測試失敗: {e}")
