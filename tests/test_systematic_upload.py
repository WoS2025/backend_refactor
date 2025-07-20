import pytest
import requests
import time
import base64
import os
import glob
import uuid
from test_workspace_manager import get_jwt

class TestSystematicUpload:
    """系統化檔案上傳測試 - 按順序處理所有檔案"""
    
    BASE_URL = "http://127.0.0.1:5000"
    WORKSPACE_URL = f"{BASE_URL}/user/workspaces"
    
    # 資料夾路徑
    COVID_DATA_FOLDER = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "COVID-19", "COVID-19")
    FEDERATED_DATA_FOLDER = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "Federated")
    
    @staticmethod
    def create_workspace(name_suffix):
        """創建測試工作區"""
        jwt = get_jwt()
        if not jwt:
            return None
            
        headers = {"Authorization": f"Bearer {jwt}"}
        
        unique_suffix = str(uuid.uuid4())[:8]
        workspace_name = f"systematic_{name_suffix}_{unique_suffix}"
        
        workspace_data = {"name": workspace_name}
        
        response = requests.post(TestSystematicUpload.WORKSPACE_URL, 
                               headers=headers, 
                               json=workspace_data)
        
        if response.status_code == 201:
            response_data = response.json()
            workspace_id = (response_data.get('workspace_id') or 
                          response_data.get('id') or 
                          (response_data.get('workspace', {}).get('workspace_id')))
            print(f"創建工作區: {workspace_name} -> {workspace_id}")
            return workspace_id
        else:
            print(f"創建工作區失敗: {response.text}")
            return None
    
    @staticmethod
    def upload_files_to_workspace(workspace_id, files, batch_name):
        """上傳檔案到工作區"""
        jwt = get_jwt()
        if not jwt:
            return False
            
        headers = {"Authorization": f"Bearer {jwt}"}
        
        try:
            file_response = requests.put(
                f"{TestSystematicUpload.WORKSPACE_URL}/{workspace_id}/files",
                headers=headers,
                json={"file": files}
            )
            
            if file_response.status_code == 200:
                print(f"✅ {batch_name} 上傳成功: {len(files)} 個檔案")
                return True
            else:
                print(f"❌ {batch_name} 上傳失敗: {file_response.text}")
                return False
                
        except Exception as e:
            print(f"❌ {batch_name} 上傳時發生錯誤: {e}")
            return False
    
    @staticmethod
    def wait_for_analysis(workspace_id, batch_name):
        """等待分析完成"""
        jwt = get_jwt()
        if not jwt:
            return False
            
        headers = {"Authorization": f"Bearer {jwt}"}
        
        print(f"等待 {batch_name} 分析完成...")
        max_wait_time = 90
        wait_interval = 10
        
        for wait_count in range(max_wait_time // wait_interval):
            print(f"  等待中... {wait_count * wait_interval} 秒")
            time.sleep(wait_interval)
            
            try:
                response = requests.get(
                    f"{TestSystematicUpload.WORKSPACE_URL}/{workspace_id}/analysis/all",
                    headers=headers
                )
                
                if response.status_code == 200:
                    results = response.json()
                    if isinstance(results, dict) and any(results.values()):
                        print(f"✅ {batch_name} 分析完成")
                        return True
                        
            except Exception as e:
                print(f"檢查 {batch_name} 分析狀態時出錯: {e}")
        
        print(f"⚠️ {batch_name} 分析超時")
        return False
    
    @staticmethod
    def process_files_in_batches(folder_path, folder_name, files_per_batch=2):
        """批次處理資料夾中的所有檔案"""
        if not os.path.exists(folder_path):
            print(f"資料夾不存在: {folder_path}")
            return []
        
        txt_files = sorted(glob.glob(os.path.join(folder_path, "*.txt")))
        print(f"\n📁 {folder_name} 資料夾: 找到 {len(txt_files)} 個 .txt 檔案")
        
        results = []
        
        # 按批次處理檔案
        for batch_start in range(0, len(txt_files), files_per_batch):
            batch_end = min(batch_start + files_per_batch, len(txt_files))
            batch_files = txt_files[batch_start:batch_end]
            batch_num = (batch_start // files_per_batch) + 1
            
            print(f"\n📦 處理 {folder_name} 批次 {batch_num}")
            
            # 準備此批次的檔案
            files_to_upload = []
            total_size = 0
            
            for i, txt_file in enumerate(batch_files):
                try:
                    with open(txt_file, 'r', encoding='utf-8') as f:
                        file_content = f.read()
                    
                    file_size = len(file_content)
                    total_size += file_size
                    
                    print(f"  {i+1}. {os.path.basename(txt_file)} ({file_size:,} 字符)")
                    
                    encoded_content = base64.b64encode(file_content.encode()).decode()
                    
                    files_to_upload.append({
                        "name": os.path.basename(txt_file),
                        "content": encoded_content
                    })
                    
                except Exception as e:
                    print(f"  ❌ 處理 {txt_file} 失敗: {e}")
                    continue
            
            # 檢查批次大小
            encoded_size = sum(len(f["content"]) for f in files_to_upload)
            size_mb = encoded_size / (1024 * 1024)
            
            print(f"  📏 批次大小: {total_size:,} 字符 / {size_mb:.2f} MB (編碼後)")
            
            if size_mb > 15:  # 超過15MB則跳過此批次
                print(f"  ⚠️ 批次過大，跳過")
                continue
            
            if not files_to_upload:
                print(f"  ⚠️ 批次中無可用檔案")
                continue
            
            # 創建工作區並上傳
            batch_name = f"{folder_name}_batch_{batch_num}"
            workspace_id = TestSystematicUpload.create_workspace(batch_name.lower())
            
            if workspace_id:
                upload_success = TestSystematicUpload.upload_files_to_workspace(
                    workspace_id, files_to_upload, batch_name
                )
                
                if upload_success:
                    analysis_success = TestSystematicUpload.wait_for_analysis(workspace_id, batch_name)
                    
                    results.append({
                        'batch_name': batch_name,
                        'workspace_id': workspace_id,
                        'files': [f['name'] for f in files_to_upload],
                        'upload_success': True,
                        'analysis_success': analysis_success,
                        'size_mb': size_mb
                    })
                else:
                    results.append({
                        'batch_name': batch_name,
                        'workspace_id': workspace_id,
                        'files': [f['name'] for f in files_to_upload],
                        'upload_success': False,
                        'analysis_success': False,
                        'size_mb': size_mb
                    })
            
            # 批次間休息
            time.sleep(3)
        
        return results

    def test_covid_systematic_upload(self):
        """系統化測試所有COVID-19檔案"""
        print("\n" + "="*60)
        print("🦠 開始系統化COVID-19檔案上傳測試")
        print("="*60)
        
        results = self.process_files_in_batches(
            self.COVID_DATA_FOLDER, 
            "COVID19", 
            files_per_batch=3  # COVID檔案較小，每批次3個
        )
        
        # 統計結果
        total_batches = len(results)
        successful_uploads = sum(1 for r in results if r['upload_success'])
        successful_analyses = sum(1 for r in results if r['analysis_success'])
        
        print(f"\n📊 COVID-19 測試統計:")
        print(f"   總批次: {total_batches}")
        print(f"   成功上傳: {successful_uploads}/{total_batches}")
        print(f"   成功分析: {successful_analyses}/{total_batches}")
        
        # 顯示詳細結果
        for result in results[:3]:  # 只顯示前3個批次的詳細信息
            print(f"\n   {result['batch_name']}:")
            print(f"     工作區: {result['workspace_id']}")
            print(f"     檔案: {result['files']}")
            print(f"     大小: {result['size_mb']:.2f} MB")
            print(f"     狀態: {'✅' if result['analysis_success'] else '❌'}")
        
        assert successful_uploads > 0, "至少要有一個批次上傳成功"

    def test_federated_systematic_upload(self):
        """系統化測試所有Federated檔案"""
        print("\n" + "="*60)
        print("🔗 開始系統化Federated檔案上傳測試")
        print("="*60)
        
        results = self.process_files_in_batches(
            self.FEDERATED_DATA_FOLDER, 
            "Federated", 
            files_per_batch=1  # Federated檔案較大，每批次1個
        )
        
        # 統計結果
        total_batches = len(results)
        successful_uploads = sum(1 for r in results if r['upload_success'])
        successful_analyses = sum(1 for r in results if r['analysis_success'])
        
        print(f"\n📊 Federated 測試統計:")
        print(f"   總批次: {total_batches}")
        print(f"   成功上傳: {successful_uploads}/{total_batches}")
        print(f"   成功分析: {successful_analyses}/{total_batches}")
        
        # 顯示詳細結果
        for result in results:
            print(f"\n   {result['batch_name']}:")
            print(f"     工作區: {result['workspace_id']}")
            print(f"     檔案: {result['files']}")
            print(f"     大小: {result['size_mb']:.2f} MB")
            print(f"     狀態: {'✅' if result['analysis_success'] else '❌'}")
        
        assert successful_uploads > 0, "至少要有一個批次上傳成功"

if __name__ == "__main__":
    test_instance = TestSystematicUpload()
    
    print("🚀 開始系統化檔案上傳測試")
    
    try:
        test_instance.test_covid_systematic_upload()
        test_instance.test_federated_systematic_upload()
        print("\n🎉 所有系統化測試完成！")
    except Exception as e:
        print(f"\n💥 測試過程中出現錯誤: {e}")
