from flask import Blueprint, request, jsonify
from infrastructure.repositories.workspaceRepo import WorkspaceRepo
import uuid
from datetime import datetime

class WorkspaceService:
    def __init__(self):
        self.repo = WorkspaceRepo()

    def get_workspaces(self):
        return self.repo.get_workspaces()

    def create_workspace(self, name):
        if self.repo.workspace_name_exists(name):
            return {"status": "error", "message": "The name already exists"}, 400
        workspace_id = str(uuid.uuid4())
        workspace = self.repo.create_workspace(id=workspace_id, name=name)
        if workspace:
            return {"status": "success", "message": "Workspace created successfully", "workspace": workspace.to_dict()}, 201
        return {"status": "error", "message": "Failed to create workspace"}, 500

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
        pass

