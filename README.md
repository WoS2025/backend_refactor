# 📌 使用者 API 文件

## 📖 目錄
1. [簡介](#簡介)
2. [基本 URL](#基本-url)
3. [API 端點](#api-端點)
   - [測試 API](#1-測試-api)
   - [註冊使用者](#2-註冊使用者)
   - [使用者登入](#3-使用者登入)
   - [忘記密碼](#4-忘記密碼)
   - [更新密碼](#5-更新密碼)
   - [取得使用者的工作空間](#6-取得使用者的工作空間)
   - [透過 Email 獲取使用者資訊](#7-透過-email-獲取使用者資訊-需-jwt)
   - [為使用者新增工作空間](#8-為使用者新增工作空間)
   - [移除使用者的工作空間](#9-移除使用者的工作空間)
4. [驗證機制](#🔐-驗證機制)

---

## 🔍 簡介
本文件提供使用者服務的 API 端點詳細資訊，包括請求方法、請求 Body 以及回應格式。

## 🌐 基本 URL
```
https://backend-refactor-nqz1.onrender.com
```

---

## ⚡ API 端點

### 1️⃣ 測試 API
#### **GET /**
📝 **描述：** 測試 API 是否正常運行。

✅ **回應範例：**
```json
"Hello, user!"
```

---

### 2️⃣ 註冊使用者
#### **POST /register**
📝 **描述：** 註冊新使用者。

📩 **請求 Body：**
```json
{
  "username": "exampleUser",
  "email": "user@example.com",
  "password": "securepassword"
}
```

✅ **回應範例：**
```json
{
  "status": "success",
  "message": "使用者註冊成功"
}
```

---

### 3️⃣ 使用者登入
#### **POST /login**
📝 **描述：** 驗證使用者身份並返回 JWT 令牌。

📩 **請求 Body：**
```json
{
  "email": "user@example.com",
  "password": "securepassword"
}
```

✅ **回應範例：**
```json
{
  "status": "success",
  "jwt": "your-jwt-token",
  "user": {
    "user_id": "12345",
    "username": "exampleUser",
    "email": "user@example.com"
  }
}
```

---

### 4️⃣ 忘記密碼
#### **POST /user/forgot-password**
📝 **描述：** 發送重設密碼的郵件。

📩 **請求 Body：**
```json
{
  "email": "user@example.com"
}
```

✅ **回應範例：**
```json
{
  "status": "success",
  "message": "密碼重設郵件已發送"
}
```

---

### 5️⃣ 更新密碼
#### **POST /user/<email>/update-password**
📝 **描述：** 更新使用者密碼。

📩 **請求 Body：**
```json
{
  "password": "newsecurepassword"
}
```

✅ **回應範例：**
```json
{
  "status": "success",
  "message": "密碼更新成功"
}
```

---

### 6️⃣ 取得使用者的工作空間
#### **GET /<user_id>**
📝 **描述：** 獲取使用者詳細資訊及其關聯的工作空間。

✅ **回應範例：**
```json
{
  "status": "success",
  "user": {
    "user_id": "12345",
    "username": "exampleUser",
    "email": "user@example.com",
    "workspace_ids": ["workspace1", "workspace2"]
  },
  "jwt": "your-jwt-token"
}
```

---

### 7️⃣ 透過 Email 獲取使用者資訊 (需 JWT)
#### **GET /email/<email>**
📝 **描述：** 透過 Email 獲取使用者資訊 (需要 JWT 令牌)。

🔐 **請求標頭：**
```
Authorization: Bearer <your-jwt-token>
```

✅ **回應範例：**
```json
{
  "status": "success",
  "user": {
    "user_id": "12345",
    "username": "exampleUser",
    "email": "user@example.com"
  }
}
```

---

### 8️⃣ 為使用者新增工作空間
#### **GET /<user_id>/workspace/<workspace_id>**
📝 **描述：** 新增工作空間至使用者帳戶。

✅ **回應範例：**
```json
{
  "status": "success",
  "message": "工作空間新增成功"
}
```

---

### 9️⃣ 移除使用者的工作空間
#### **DELETE /<user_id>/workspace/<workspace_id>**
📝 **描述：** 從使用者帳戶中移除工作空間。

✅ **回應範例：**
```json
{
  "status": "success",
  "message": "工作空間移除成功"
}
```

---

## 🔐 驗證機制
部分 API 需要身份驗證，請在請求標頭中加入 JWT 令牌：
```
Authorization: Bearer <your-jwt-token>
```

