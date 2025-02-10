from domain.models.workspace import Workspace

class AnalysisService:
    def __init__(self):
        pass

    def get_result(self, workspace: Workspace):
        # Example analysis: count the number of files in the workspace
        num_files = len(workspace.files)
        
        # Example analysis: list all file names
        file_names = [file['name'] for file in workspace.files]
        
        result = {
            'workspace_id': workspace.workspace_id,
            'workspace_name': workspace.name,
            'num_files': num_files,
            'file_names': file_names
        }
        
        return result