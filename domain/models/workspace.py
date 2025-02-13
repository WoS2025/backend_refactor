class Workspace:
    def __init__(self, workspace_id, name, created_at, files=None, latest_result=None):
        self.workspace_id = workspace_id
        self.name = name
        self.created_at = created_at
        self.files = files if files is not None else []
        self.latest_result = latest_result
        
    def add_file(self, file_name):
        self.files.append(file_name)
    
    def remove_file(self, file_name):
        # print(self.files)
        self.files = [file for file in self.files if file['name'] != file_name]
        # print(self.files)
    def to_dict(self):
        return {
            'workspace_id': self.workspace_id,
            'name': self.name,
            'created_at': self.created_at,
            'files': self.files,
            'latest_result': self.latest_result
        }