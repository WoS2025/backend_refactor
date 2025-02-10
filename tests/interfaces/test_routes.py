def test_home(client):
    response = client.get('/')
    assert response.status_code == 200
    assert response.data == b"Hello, World!"

def test_create_workspace(client):
    response = client.post('/workspaces', json={'name': 'Test Workspace'})
    assert response.status_code == 201
    data = response.get_json()
    assert 'workspace_id' in data

def test_get_workspaces(client):
    response = client.get('/workspaces')
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)

def test_get_workspace(client):
    # First, create a workspace
    create_response = client.post('/workspaces', json={'name': 'Test Workspace'})
    workspace_id = create_response.get_json()['workspace_id']

    # Then, get the created workspace
    response = client.get(f'/workspaces/{workspace_id}')
    assert response.status_code == 200
    data = response.get_json()
    assert data['workspace_id'] == workspace_id

def test_delete_workspace(client):
    # First, create a workspace
    create_response = client.post('/workspaces', json={'name': 'Test Workspace'})
    workspace_id = create_response.get_json()['workspace_id']

    # Then, delete the created workspace
    response = client.delete(f'/workspaces/{workspace_id}')
    assert response.status_code == 204

    # Verify the workspace is deleted
    get_response = client.get(f'/workspaces/{workspace_id}')
    assert get_response.status_code == 404

def test_add_file_to_workspace(client):
    # First, create a workspace
    create_response = client.post('/workspaces', json={'name': 'Test Workspace'})
    workspace_id = create_response.get_json()['workspace_id']

    # Then, add a file to the created workspace
    response = client.post(f'/workspaces/{workspace_id}/files', json={'file': {'name': 'test_file.txt', 'content': 'test content'}})
    assert response.status_code == 204

    # Verify the file is added
    get_response = client.get(f'/workspaces/{workspace_id}')
    data = get_response.get_json()
    assert any(file['name'] == 'test_file.txt' for file in data['files'])

def test_remove_file_from_workspace(client):
    # First, create a workspace
    create_response = client.post('/workspaces', json={'name': 'Test Workspace'})
    workspace_id = create_response.get_json()['workspace_id']

    # Add a file to the created workspace
    client.post(f'/workspaces/{workspace_id}/files', json={'file': {'name': 'test_file.txt', 'content': 'test content'}})

    # Then, remove the file from the workspace
    response = client.delete(f'/workspaces/{workspace_id}/files/test_file.txt')
    assert response.status_code == 204

    # Verify the file is removed
    get_response = client.get(f'/workspaces/{workspace_id}')
    data = get_response.get_json()
    assert not any(file['name'] == 'test_file.txt' for file in data['files'])