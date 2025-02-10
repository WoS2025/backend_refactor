from infrastructure.repositories import Database
from domain.models.workspace import Workspace
from datetime import datetime
class WorkspaceRepo:
    def __init__(self):
        self.db = Database()

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

    def create_workspace(self, id, name):
        data = self.db.add_workspace(id, name)
        if data and data.inserted_id:
            return Workspace(workspace_id=id, name=name, files=[], created_at=datetime.now())
        return None

    def update_workspace(self, workspace):
        collection = self.db.get_collection('workspaces')
        return collection.update_one({'workspace_id': workspace.workspace_id}, {'$set': workspace.to_dict()})

    def delete_workspace(self, workspace_id):
        collection = self.db.get_collection('workspaces')
        return collection.delete_one({'workspace_id': workspace_id})

    def workspace_name_exists(self, name):
        collection = self.db.get_collection('workspaces')
        return collection.find_one({'name': name}) is not None