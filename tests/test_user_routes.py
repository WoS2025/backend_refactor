# === test_user_routes.py ===
import pytest
import requests

BASE_URL = "http://127.0.0.1:5000/user"
EXISTING_USER_ID = "fb0965e5-2288-48a7-be44-ffb6fe4e5b36"
EXISTING_USER_EMAIL = "zxcv7898@gmail.com"
EXISTING_USER_PASSWORD = "zxcv7898"
EXISTING_WORKSPACE_ID = "200270e4-2982-4091-8424-e3817969ca80"

def get_jwt():
    payload = {"email": EXISTING_USER_EMAIL, "password": EXISTING_USER_PASSWORD}
    response = requests.post(f"{BASE_URL}/login", json=payload)
    return response.json().get("jwt")

def test_home():
    r = requests.get(f"{BASE_URL}/")
    assert r.status_code == 200 and r.text == "Hello, user!"

def test_register():
    payload = {"username": "testuser", "email": "testuser@example.com", "password": "securepassword123"}
    r = requests.post(f"{BASE_URL}/register", json=payload)
    assert r.status_code in [200, 400]

def test_login():
    payload = {"email": EXISTING_USER_EMAIL, "password": EXISTING_USER_PASSWORD}
    r = requests.post(f"{BASE_URL}/login", json=payload)
    data = r.json()
    assert r.status_code == 200 and data["status"] == "success" and "jwt" in data

def test_get_user_by_email():
    jwt = get_jwt()
    assert jwt, "JWT required"
    headers = {"Authorization": f"Bearer {jwt}"}
    r = requests.get(f"{BASE_URL}/email/{EXISTING_USER_EMAIL}", headers=headers)
    assert r.status_code == 200 and r.json()["status"] == "success"

def test_get_user_workspaces():
    r = requests.get(f"{BASE_URL}/{EXISTING_USER_ID}")
    data = r.json()
    assert data['status'] == 'success' and data['user']['email'] == EXISTING_USER_EMAIL

def test_get_user_workspaces_fail():
    r = requests.get(f"{BASE_URL}/invalid-id")
    assert r.status_code == 400 or r.json().get('status') == 'error'

def test_forgot_password():
    r = requests.post(f"{BASE_URL}/user/forgot-password", json={"email": EXISTING_USER_EMAIL})
    assert r.status_code == 200

def test_update_password():
    r = requests.post(f"{BASE_URL}/user/{EXISTING_USER_EMAIL}/update-password", json={"password": "newpass123"})
    assert r.status_code in [200, 400]

def test_add_workspace():
    r = requests.get(f"{BASE_URL}/{EXISTING_USER_ID}/workspace/workspace123")
    assert r.status_code == 200

def test_remove_workspace():
    r = requests.delete(f"{BASE_URL}/{EXISTING_USER_ID}/workspace/workspace123")
    assert r.status_code == 200

# === ANALYSIS ===

def post_analysis(endpoint, payload):
    return requests.post(f"{BASE_URL}/{endpoint}?workspace_id={EXISTING_WORKSPACE_ID}", json=payload)

def test_keyword_analysis():
    r = post_analysis("keyword", {"keyword": "AI"})
    assert r.status_code in [200, 404]

def test_keyword_year():
    r = post_analysis("keyword/year", {"start": 2015, "end": 2023, "threshold": 5})
    assert r.status_code in [200, 404]

def test_keyword_occurrence():
    r = post_analysis("keyword/occurence", {"threshold": 3})
    assert r.status_code in [200, 404]

def test_author_year():
    r = post_analysis("author/year", {"start": 2015, "end": 2023, "threshold": 2})
    assert r.status_code in [200, 404]

def test_reference():
    r = post_analysis("reference", {"threshold": 10})
    assert r.status_code in [200, 404]

def test_field():
    r = post_analysis("field", {"field": "Computer Science"})
    assert r.status_code in [200, 404]

def test_field_year():
    r = post_analysis("field/year", {"start": 2010, "end": 2022, "threshold": 3})
    assert r.status_code in [200, 404]

def test_field_occurrence():
    r = post_analysis("field/occurence", {"threshold": 5})
    assert r.status_code in [200, 404]

def test_country_year():
    r = post_analysis("country/year", {"start": 2010, "end": 2022, "threshold": 3})
    assert r.status_code in [200, 404]

def test_institution():
    r = post_analysis("institution", {"start": 2010, "end": 2022, "threshold": 2})
    assert r.status_code in [200, 404]

def test_institution_year():
    r = post_analysis("institution/year", {"start": 2010, "end": 2022, "threshold": 3})
    assert r.status_code in [200, 404]

def test_result():
    r = requests.get(f"{BASE_URL}/result?workspace_id={EXISTING_WORKSPACE_ID}")
    assert r.status_code in [200, 404]

def test_download():
    r = requests.get(f"{BASE_URL}/download?workspace_id={EXISTING_WORKSPACE_ID}")
    assert r.status_code in [200, 404]
