import json
import os
from unittest import result
from flask import Blueprint, request, jsonify
from infrastructure.repositories.workspaceRepo import WorkspaceRepo
from infrastructure.repositories.analysisRepo import AnalysisRepo
from service.keyword_analysis import KeywordAnalysis
from service.author_analysis import AuthorAnalysis
from service.reference_analysis import ReferenceAnalysis
from service.field_analysis import FieldAnalysis
from service.university_analysis import InstitutionAnalysis
from service.country_analysis import CountryAnalysis
import uuid
from datetime import datetime
import base64

class WorkspaceService:
    def __init__(self):
        self.repo = WorkspaceRepo()
        self.analysis_repo = AnalysisRepo()

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
        # Decode the Base64-encoded content
        if 'content' in file:
            file['content'] = base64.b64decode(file['content']).decode('utf-8')
        workspace = self.repo.get_workspace(workspace_id)
        if workspace:
            workspace.add_file(file)
            update_result = self.repo.update_workspace(workspace)
            if update_result.modified_count > 0:
                # 文件添加成功後，自動執行所有分析
                self._run_all_analysis(workspace_id)
                return True
        return False

    def remove_file_from_workspace(self, workspace_id, file_name):
        workspace = self.repo.get_workspace(workspace_id)
        if workspace:
            workspace.remove_file(file_name)
            update_result = self.repo.update_workspace(workspace)
            return update_result.modified_count > 0
        return False

    def get_analysis(self, workspace_id):
        workspace = self.repo.get_workspace(workspace_id)
        if workspace:
            if workspace.latest_result:
                return workspace.latest_result       
        return None

    def save_analysis_to_file(self, workspace_id, analysis):
        # 假設結果存儲為 JSON 格式
        file_path = f'temp/analysis_{workspace_id}.json'

        # 確保 temp 資料夾存在
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        # 將結果保存為 JSON 檔案
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=4)

        return file_path

    def keyword_analysis(self, workspace_id, keyword):
        workspace = self.repo.get_workspace(workspace_id)
        if workspace:
            files = workspace.files
            count, conditionCount, start, end, results = KeywordAnalysis.keywordEachYear(files, files, keyword)
            workspace.latest_result = {
                'type': 'keyword_analysis',
                'count': count,
                'conditionCount': conditionCount,
                'start': start,
                'end': end,
                'results': results
            }
            self.repo.update_workspace(workspace)
            return workspace.latest_result
        return None
    
    def keyword_analysis_year(self, workspace_id, start, end, threshold):
        workspace = self.repo.get_workspace(workspace_id)
        if workspace:
            files = workspace.files
            count, conditionCount, results = KeywordAnalysis.year(files, files, start, end, threshold)
            workspace.latest_result = {
                'type': 'keyword_analysis_year',
                'count': count,
                'conditionCount': conditionCount,
                'results': results
            }
            self.repo.update_workspace(workspace)
            return workspace.latest_result
        return None
    
    def keyword_analysis_occurence(self, workspace_id, threshold):
        workspace = self.repo.get_workspace(workspace_id)
        if workspace:
            files = workspace.files
            titleCount, results = KeywordAnalysis.keywordOccurence(files, files, threshold)
            workspace.latest_result = {
                'type': 'keyword_analysis_occurence',
                'titleCount': titleCount,
                'results': results
            }
            self.repo.update_workspace(workspace)
            return workspace.latest_result
        return None
    
    # 根據年份區間對作者做分析（看年份區間內作者發表了幾篇）
    def author_analysis_year(self, workspace_id, start, end, threshold):
        workspace = self.repo.get_workspace(workspace_id)
        if workspace:
            files = workspace.files
            count, conditionCount, results = AuthorAnalysis.author(files, files, start, end, threshold)
            workspace.latest_result = {
                'type': 'author_analysis',
                'count': count,
                'conditionCount': conditionCount,
                'conditionCount': conditionCount,
                'results': results
            }
            self.repo.update_workspace(workspace)
            return workspace.latest_result
        return None
    
    # 根據引用次數做分析
    def reference_analysis(self, workspace_id, threshold):
        workspace = self.repo.get_workspace(workspace_id)
        if workspace:
            files = workspace.files
            count, results = ReferenceAnalysis.get_referencesInfo(files, files, threshold)
            workspace.latest_result = {
                'type': 'reference_analysis',
                'count': count,
                'results': results
            }
            self.repo.update_workspace(workspace)
            return workspace.latest_result
        return None
    
    def field_analysis(self, workspace_id, field):
        workspace = self.repo.get_workspace(workspace_id)
        if workspace:
            files = workspace.files
            count, conditionCount, start, end, results = FieldAnalysis.fieldField(files, files, field)
            workspace.latest_result = {
                'type': 'field_analysis',
                'count': count,
                'conditionCount': conditionCount,
                'start': start,
                'end': end,
                'results': results
            }
            self.repo.update_workspace(workspace)
            return workspace.latest_result
        return None
    
    def field_analysis_year(self, workspace_id, start, end, threshold):
        workspace = self.repo.get_workspace(workspace_id)
        if workspace:
            files = workspace.files
            count, conditionCount, results = FieldAnalysis.fieldEachYear(files, files, start, end, threshold)
            workspace.latest_result = {
                'type': 'field_analysis_year',
                'count': count,
                'conditionCount': conditionCount,
                'results': results
            }
            self.repo.update_workspace(workspace)
            return workspace.latest_result
        return None
    
    def field_analysis_occurence(self, workspace_id, threshold):
        workspace = self.repo.get_workspace(workspace_id)
        if workspace:
            files = workspace.files
            titleCount, results = FieldAnalysis.fieldOccurence(files, files, threshold)
            workspace.latest_result = {
                'type': 'field_analysis_occurence',
                'titleCount': titleCount,
                'results': results
            }
            self.repo.update_workspace(workspace)
            return workspace.latest_result
        return None

    
    def country_analysis_year(self, workspace_id, start, end, threshold):
        workspace = self.repo.get_workspace(workspace_id)
        if workspace:
            files = workspace.files
            count, conditionCount, results = CountryAnalysis.country_analysis_by_year(files, files, start, end, threshold)
            workspace.latest_result = {
                'type': 'country_analysis_year',
                'count': count,
                'conditionCount': conditionCount,
                'results': results
            }
            self.repo.update_workspace(workspace)
            return workspace.latest_result
        return None
    
    #透過 WorkspaceService 獲取 workspace（工作區），並提取工作區內的文件並執行學校分析
    def institution_analysis(self, workspace_id, start, end, threshold):
        workspace = self.repo.get_workspace(workspace_id)
        if workspace:
            files = workspace.files
            # count, conditionCount, results 
            count, conditionCount, results_institutions, results_publishers = InstitutionAnalysis.analyze(files, start, end, threshold)
            workspace.latest_result = {
                'type': 'institution_analysis',
                'count': count,
                'conditionCount': conditionCount,
                'results_institutions': results_institutions,
                'results_publishers': results_publishers
            }
            self.repo.update_workspace(workspace)
            return workspace.latest_result
        return None
    
    def institution_analysis_year(self, workspace_id, start, end, threshold):
        workspace = self.repo.get_workspace(workspace_id)
        if workspace:
            files = workspace.files
            result = InstitutionAnalysis.institution_analysis_by_year(files, start, end, threshold)
            workspace.latest_result = {
                'type': 'institution_analysis_year',
                'results': result
            }
            self.repo.update_workspace(workspace)
            return workspace.latest_result
        return None
    
    def _run_all_analysis(self, workspace_id):
        """執行所有分析功能並保存結果"""
        workspace = self.repo.get_workspace(workspace_id)
        if not workspace or not workspace.files:
            return

        # 預設參數
        default_params = {
            'start': 2000,
            'end': 2025,
            'threshold': 1
        }

        try:
            # 1. 關鍵字出現次數分析
            try:
                result = self.keyword_analysis_occurence(workspace_id, default_params['threshold'])
                if result:
                    self.analysis_repo.save_analysis(workspace_id, 'keyword_occurence', result)
                    print(f"✓ keyword_occurence analysis completed for workspace {workspace_id}")
                else:
                    print(f"✗ keyword_occurence analysis returned no result for workspace {workspace_id}")
            except Exception as e:
                print(f"✗ keyword_occurence analysis error for workspace {workspace_id}: {str(e)}")

            # 2. 作者年份分析
            try:
                result = self.author_analysis_year(workspace_id, default_params['start'], default_params['end'], default_params['threshold'])
                if result:
                    self.analysis_repo.save_analysis(workspace_id, 'author_year', result)
                    print(f"✓ author_year analysis completed for workspace {workspace_id}")
                else:
                    print(f"✗ author_year analysis returned no result for workspace {workspace_id}")
            except Exception as e:
                print(f"✗ author_year analysis error for workspace {workspace_id}: {str(e)}")

            # 3. 引用分析
            try:
                result = self.reference_analysis(workspace_id, default_params['threshold'])
                if result:
                    self.analysis_repo.save_analysis(workspace_id, 'reference', result)
                    print(f"✓ reference analysis completed for workspace {workspace_id}")
                else:
                    print(f"✗ reference analysis returned no result for workspace {workspace_id}")
            except Exception as e:
                print(f"✗ reference analysis error for workspace {workspace_id}: {str(e)}")

            # 4. 領域出現次數分析
            try:
                result = self.field_analysis_occurence(workspace_id, default_params['threshold'])
                if result:
                    self.analysis_repo.save_analysis(workspace_id, 'field_occurence', result)
                    print(f"✓ field_occurence analysis completed for workspace {workspace_id}")
                else:
                    print(f"✗ field_occurence analysis returned no result for workspace {workspace_id}")
            except Exception as e:
                print(f"✗ field_occurence analysis error for workspace {workspace_id}: {str(e)}")

            # 5. 領域年份分析
            try:
                result = self.field_analysis_year(workspace_id, default_params['start'], default_params['end'], default_params['threshold'])
                if result:
                    self.analysis_repo.save_analysis(workspace_id, 'field_year', result)
                    print(f"✓ field_year analysis completed for workspace {workspace_id}")
                else:
                    print(f"✗ field_year analysis returned no result for workspace {workspace_id}")
            except Exception as e:
                print(f"✗ field_year analysis error for workspace {workspace_id}: {str(e)}")

            # 6. 機構分析
            try:
                result = self.institution_analysis(workspace_id, default_params['start'], default_params['end'], default_params['threshold'])
                if result:
                    self.analysis_repo.save_analysis(workspace_id, 'institution', result)
                    print(f"✓ institution analysis completed for workspace {workspace_id}")
                else:
                    print(f"✗ institution analysis returned no result for workspace {workspace_id}")
            except Exception as e:
                print(f"✗ institution analysis error for workspace {workspace_id}: {str(e)}")

            # 7. 機構年份分析
            try:
                result = self.institution_analysis_year(workspace_id, default_params['start'], default_params['end'], default_params['threshold'])
                if result:
                    self.analysis_repo.save_analysis(workspace_id, 'institution_year', result)
                    print(f"✓ institution_year analysis completed for workspace {workspace_id}")
                else:
                    print(f"✗ institution_year analysis returned no result for workspace {workspace_id}")
            except Exception as e:
                print(f"✗ institution_year analysis error for workspace {workspace_id}: {str(e)}")

            # 8. 國家年份分析
            try:
                result = self.country_analysis_year(workspace_id, default_params['start'], default_params['end'], default_params['threshold'])
                if result:
                    self.analysis_repo.save_analysis(workspace_id, 'country_year', result)
                    print(f"✓ country_year analysis completed for workspace {workspace_id}")
                else:
                    print(f"✗ country_year analysis returned no result for workspace {workspace_id}")
            except Exception as e:
                print(f"✗ country_year analysis error for workspace {workspace_id}: {str(e)}")

        except Exception as e:
            print(f"General analysis error for workspace {workspace_id}: {str(e)}")

    def get_all_analysis_results(self, workspace_id):
        """獲取工作區的所有最新分析結果"""
        return self.analysis_repo.get_latest_analysis(workspace_id)

    def get_analysis_by_type(self, workspace_id, analysis_type):
        """根據類型獲取分析結果"""
        results = self.analysis_repo.get_analysis(workspace_id, analysis_type)
        return results[-1] if results else None

