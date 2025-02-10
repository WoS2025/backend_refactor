from infrastructure.repositories import Database
from domain.models.workspace import Workspace

class WorkspaceRepo:
    def __init__(self, db):
        self.db = db

    def get_workspace(self, workspace_id):
        collection = self.db.get_collection('workspaces')
        data = collection.find_one({'workspace_id': workspace_id})
        if data:
            data['workspace_id'] = str(data['workspace_id'])
            if '_id' in data:
                del data['_id']
            return Workspace(**data)
        return None

    def get_workspaces(self):
        collection = self.db.get_collection('workspaces')
        workspaces = []
        for data in collection.find():
            data['workspace_id'] = str(data['workspace_id'])
            if '_id' in data:
                del data['_id']
            workspaces.append(Workspace(**data))
        return workspaces

    def create_workspace(self, workspace):
        collection = self.db.get_collection('workspaces')
        result = collection.insert_one(workspace.to_dict())
        return workspace.workspace_id

    def update_workspace(self, workspace):
        collection = self.db.get_collection('workspaces')
        return collection.update_one({'workspace_id': workspace.workspace_id}, {'$set': workspace.to_dict()})

    def delete_workspace(self, workspace_id):
        collection = self.db.get_collection('workspaces')
        return collection.delete_one({'workspace_id': workspace_id})