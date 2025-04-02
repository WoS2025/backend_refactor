# 📌 後端 API (26 個端點)

## 📍 基本資訊  
**Base URL**: `https://backend-refactor-nqz1.onrender.com`  
所有路徑參數需替換為實際值（如 `workspace_id`），錯誤回應皆包含 `error` 字段說明原因。

---

## 📖 完整目錄 (點擊跳轉)
### 👤 用戶相關 API (7 個)
1. [註冊](#-註冊)  
2. [登入](#-登入)  
3. [忘記密碼](#-忘記密碼)  
4. [更新密碼](#-更新密碼)  
5. [綁定工作區至用戶](#-綁定工作區至用戶)  
6. [移除用戶工作區](#-移除用戶工作區)  
7. [獲取用戶工作區](#-獲取用戶工作區)  

### 📂 工作區管理 API (7 個)
1. [獲取所有工作區](#-獲取所有工作區)  
2. [創建工作區](#-創建工作區)  
3. [獲取單個工作區](#-獲取單個工作區)  
4. [刪除工作區](#-刪除工作區)  
5. [新增檔案至工作區](#-新增檔案至工作區)  
6. [刪除工作區檔案](#-刪除工作區檔案)  
7. [獲取分析結果](#-獲取分析結果)  

### 📊 分析功能 API (12 個)
1. [關鍵字分析](#-關鍵字分析)  
2. [關鍵字年份分析](#-關鍵字年份分析)  
3. [關鍵字出現次數分析](#-關鍵字出現次數分析)  
4. [作者年份分析](#-作者年份分析)  
5. [引用分析](#-引用分析)  
6. [領域分析](#-領域分析)  
7. [領域年份分析](#-領域年份分析)  
8. [領域出現次數分析](#-領域出現次數分析)  
9. [機構分析](#-機構分析)  
10. [機構年份分析](#-機構年份分析)  
11. [國家年份分析](#-國家年份分析)  
12. [下載分析結果](#-下載分析結果)  

---

## 👤 用戶相關 API

### 🔹 註冊  
- **路徑**: `POST /user/register`  
- **請求 Body**:  
  ```json
  {
    "username": "用戶名稱",
    "email": "user@example.com",
    "password": "用戶密碼"
  }
  ```
- **回應**:
  - 200 OK：註冊成功
  - 400 Bad Request：格式錯誤或欄位缺失

### 🔹 登入
- **路徑**: `POST /user/login`
- **請求 Body**:
  ```json
  {
    "email": "user@example.com",
    "password": "用戶密碼"
  }
  ```
- **回應**:
  - 200 OK：登入成功
  - 400 Bad Request：帳號密碼錯誤

### 🔹 忘記密碼
- **路徑**: `POST /user/forgot-password`
- **請求 Body**:
  ```json
  {
    "email": "user@example.com"
  }
  ```
- **回應**:
  - 200 OK：重設郵件已發送
  - 400 Bad Request：Email 格式錯誤

### 🔹 更新密碼
- **路徑**: `POST /user/<email>/update-password`
- **請求 Body**:
  ```json
  {
    "password": "新密碼"
  }
  ```
- **回應**:
  - 200 OK：密碼更新成功
  - 400 Bad Request：欄位缺失

### 🔹 綁定工作區至用戶
- **路徑**: `GET /user/<user_id>/workspace/<workspace_id>`
- **回應**:
  - 200 OK：綁定成功
  - 400 Bad Request：用戶或工作區不存在

### 🔹 移除用戶工作區
- **路徑**: `DELETE /user/<user_id>/workspace/<workspace_id>`
- **回應**:
  - 200 OK：移除成功
  - 400 Bad Request：綁定關係不存在

### 🔹 獲取用戶工作區
- **路徑**: `GET /user/<user_id>`
- **回應**:
  - 200 OK：返回用戶綁定的工作區列表
  - 400 Bad Request：用戶不存在

## 📂 工作區管理 API

### 🔹 獲取所有工作區
- **路徑**: `GET /user/workspaces`
- **回應**:
  - 200 OK：返回所有工作區資料

### 🔹 創建工作區
- **路徑**: `POST /user/workspaces`
- **請求 Body**:
  ```json
  {
    "name": "工作區名稱"
  }
  ```
- **回應**:
  - 200 OK：創建成功
  - 400 Bad Request：名稱格式錯誤（僅允許英文、數字、底線）

### 🔹 獲取單個工作區
- **路徑**: `GET /user/workspaces/<workspace_id>`
- **回應**:
  - 200 OK：返回工作區詳細資料
  - 404 Not Found：工作區不存在

### 🔹 刪除工作區
- **路徑**: `DELETE /user/workspaces/<workspace_id>`
- **回應**:
  - 204 No Content：刪除成功
  - 404 Not Found：工作區不存在

### 🔹 新增檔案至工作區
- **路徑**: `PUT /user/workspaces/<workspace_id>/files`
- **請求 Body**:
  ```json
  {
    "file": [
      { "name": "檔案1", "content": "內容" },
      { "name": "檔案2", "content": "內容" }
    ]
  }
  ```
- **回應**:
  - 204 No Content：新增成功
  - 400 Bad Request：檔案格式錯誤

### 🔹 刪除工作區檔案
- **路徑**: `DELETE /user/workspaces/<workspace_id>/files/<file_name>`
- **回應**:
  - 204 No Content：刪除成功
  - 404 Not Found：檔案不存在

### 🔹 獲取分析結果
- **路徑**: `GET /user/workspaces/<workspace_id>/analysis/result`
- **回應**:
  - 200 OK：返回分析結果
  - 404 Not Found：無結果

## 📊 分析功能 API

### 🔹 關鍵字分析
- **路徑**: `POST /workspace/workspaces/<workspace_id>/analysis/keyword`
- **請求 Body**:
  ```json
  {
    "keyword": "關鍵字"
  }
  ```
- **回應**:
  - 200 OK：返回關鍵字分析結果
  - 404 Not Found：無結果

### 🔹 關鍵字年份分析
- **路徑**: `POST /workspace/workspaces/<workspace_id>/analysis/keyword/year`
- **請求 Body**:
  ```json
  {
    "start": 2000,
    "end": 2025,
    "threshold": 1
  }
  ```
- **回應**:
  - 200 OK：返回年份趨勢分析
  - 404 Not Found：無結果

### 🔹 關鍵字出現次數分析
- **路徑**: `POST /workspace/workspaces/<workspace_id>/analysis/keyword/occurence`
- **請求 Body**:
  ```json
  {
    "threshold": 1
  }
  ```
- **回應**:
  - 200 OK：返回高頻關鍵字列表

### 🔹 作者年份分析
- **路徑**: `POST /workspace/workspaces/<workspace_id>/analysis/author/year`
- **請求 Body**:
  ```json
  {
    "start": 2000,
    "end": 2025,
    "threshold": 1
  }
  ```
- **回應**:
  - 200 OK：返回活躍作者分析

### 🔹 引用分析
- **路徑**: `POST /workspace/workspaces/<workspace_id>/analysis/reference`
- **請求 Body**:
  ```json
  {
    "threshold": 1
  }
  ```
- **回應**:
  - 200 OK：返回高引用文獻列表

### 🔹 領域分析
- **路徑**: `POST /workspace/workspaces/<workspace_id>/analysis/field`
- **請求 Body**:
  ```json
  {
    "field": "領域名稱"
  }
  ```
- **回應**:
  - 200 OK：返回領域相關分析

### 🔹 領域年份分析
- **路徑**: `POST /workspace/workspaces/<workspace_id>/analysis/field/year`
- **請求 Body**:
  ```json
  {
    "start": 2000,
    "end": 2025,
    "threshold": 1
  }
  ```
- **回應**:
  - 200 OK：返回領域發展趨勢

### 🔹 領域出現次數分析
- **路徑**: `POST /workspace/workspaces/<workspace_id>/analysis/field/occurence`
- **請求 Body**:
  ```json
  {
    "threshold": 1
  }
  ```
- **回應**:
  - 200 OK：返回高頻領域列表

### 🔹 機構分析
- **路徑**: `POST /workspace/workspaces/<workspace_id>/analysis/institution`
- **請求 Body**:
  ```json
  {
    "start": 2000,
    "end": 2025,
    "threshold": 1
  }
  ```
- **回應**:
  - 200 OK：返回機構合作分析

### 🔹 機構年份分析
- **路徑**: `POST /workspace/workspaces/<workspace_id>/analysis/institution/year`
- **請求 Body**:
  ```json
  {
    "start": 2000,
    "end": 2025,
    "threshold": 1
  }
  ```
- **回應**:
  - 200 OK：返回機構年度趨勢

### 🔹 國家年份分析
- **路徑**: `POST /workspace/workspaces/<workspace_id>/analysis/country/year`
- **請求 Body**:
  ```json
  {
    "start": 2000,
    "end": 2025,
    "threshold": 1
  }
  ```
- **回應**:
  - 200 OK：返回國家發表趨勢

### 🔹 下載分析結果
- **路徑**: `GET /workspace/workspaces/<workspace_id>/analysis/download`
- **回應**:
  - 自動下載 JSON 格式分析報告
  - 404 Not Found：無結果
