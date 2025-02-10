import pytest
from app import app
from infrastructure.repositories import Database
from infrastructure.repositories.workspaceRepo import WorkspaceRepo
#from domain.services.workspace_service import WorkspaceService
from service.workspace_service import WorkspaceService

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def service():
    db = Database()
    repo = WorkspaceRepo(db)
    return WorkspaceService(repo)