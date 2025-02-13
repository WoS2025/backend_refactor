class Workspace:
    def __init__(self, workspace_id, name, created_at, files=None, latest_result=None):
        self.workspace_id = workspace_id
        self.name = name
        self.created_at = created_at
        self.files = files if files is not None else []
        self.latest_result = latest_result
        
    def to_dict(self):
        return {
            'workspace_id': self.workspace_id,
            'name': self.name,
            'created_at': self.created_at,
            'files': self.files,
            'latest_result': self.latest_result
        }