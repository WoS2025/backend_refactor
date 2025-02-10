class Workspace:
    def __init__(self, workspace_id, name, created_at, files=None):
        self.workspace_id = workspace_id
        self.name = name
        self.created_at = created_at
        self.files = files if files is not None else []

    def add_file(self, file):
        self.files.append(file)

    def remove_file(self, file_name):
        self.files = [file for file in self.files if file['name'] != file_name]

    def to_dict(self):
        return {
            'workspace_id': self.workspace_id,
            'name': self.name,
            'created_at': self.created_at,
            'files': self.files
        }