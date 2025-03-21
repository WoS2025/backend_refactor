import pytest
import requests

def test_get_user_workspaces_success():
    response = requests.get('https://backend-refactor-nqz1.onrender.com/user/fb0965e5-2288-48a7-be44-ffb6fe4e5b36')
    response = response.json()
    print(response)
    assert response['status'] == 'success'
    assert response['user']['email'] == 'zxcv7898@gmail.com'

def test_get_user_workspaces_fail():
    response = requests.get('https://backend-refactor-nqz1.onrender.com/user/fb0965e5-2288-48a7-be44-ffb6fe4e56')
    response = response.json()
    print(response)
    assert response['status'] == 'error'
    assert response['message'] == 'User not found'