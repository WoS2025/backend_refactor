from flask import Blueprint, request, jsonify
from infrastructure.repositories.workspaceRepo import WorkspaceRepo
from domain.models.workspace import Workspace

# domain logic should be in domain/services/workspaceService.py
#from domain.services.workspaceService import WorkspaceService

import uuid
from datetime import datetime

class WorkspaceService:
    def __init__(self, repo):
        self.repo = repo

    def get_workspaces(self):
        return self.repo.get_workspaces()

    def create_workspace(self, name):
        workspace = Workspace(workspace_id=str(uuid.uuid4()), name=name, created_at=datetime.utcnow())
        return self.repo.create_workspace(workspace)

    def get_workspace(self, workspace_id):
        return self.repo.get_workspace(workspace_id)

    def delete_workspace(self, workspace_id):
        return self.repo.delete_workspace(workspace_id)

    def add_file_to_workspace(self, workspace_id, file):
        workspace = self.repo.get_workspace(workspace_id)
        if workspace:
            workspace.add_file(file)
            self.repo.update_workspace(workspace)
            return True
        return False

    def remove_file_from_workspace(self, workspace_id, file_name):
        workspace = self.repo.get_workspace(workspace_id)
        if workspace:
            workspace.remove_file(file_name)
            self.repo.update_workspace(workspace)
            return True
        return False

    def get_analysis(self, workspace_id):
        workspace = self.repo.get_workspace(workspace_id)
        if workspace:
            # Example analysis: count the number of files in the workspace
            num_files = len(workspace.files)
            file_names = [file['name'] for file in workspace.files]
            return {
                'workspace_id': workspace.workspace_id,
                'workspace_name': workspace.name,
                'num_files': num_files,
                'file_names': file_names
            }
        return None

    def get_author_analysis(self, workspace_id):
        # Implement author analysis logic here
        pass

