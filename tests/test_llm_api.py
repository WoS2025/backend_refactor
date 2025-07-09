import requests
import os

def test_llm_ask():
    base_url = os.getenv('BASE_URL', 'http://127.0.0.1:5000')
    url = f"{base_url}/llm/ask"
    payload = {"prompt": "請用中文解釋什麼是RAG？"}
    response = requests.post(url, json=payload)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    assert response.status_code == 200
    assert 'result' in response.json()
    assert len(response.json()['result']) > 0

if __name__ == "__main__":
    test_llm_ask()
