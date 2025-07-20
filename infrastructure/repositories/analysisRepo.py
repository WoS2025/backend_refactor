from infrastructure.repositories import Database
from datetime import datetime

class AnalysisRepo:
    def __init__(self):
        self.db = Database()

    def save_analysis(self, workspace_id, analysis_type, result):
        """保存分析結果"""
        collection = self.db.get_collection('analysis_results')
        analysis_data = {
            'workspace_id': workspace_id,
            'analysis_type': analysis_type,
            'result': result,
            'created_at': datetime.now()
        }
        return collection.insert_one(analysis_data)

    def get_analysis(self, workspace_id, analysis_type=None):
        """獲取分析結果"""
        collection = self.db.get_collection('analysis_results')
        query = {'workspace_id': workspace_id}
        if analysis_type:
            query['analysis_type'] = analysis_type
        return list(collection.find(query, {'_id': 0}))

    def get_latest_analysis(self, workspace_id):
        """獲取最新的所有分析結果"""
        collection = self.db.get_collection('analysis_results')
        pipeline = [
            {'$match': {'workspace_id': workspace_id}},
            {'$sort': {'created_at': -1}},
            {'$group': {
                '_id': '$analysis_type',
                'latest_result': {'$first': {
                    'workspace_id': '$workspace_id',
                    'analysis_type': '$analysis_type',
                    'result': '$result',
                    'created_at': '$created_at'
                }}
            }}
        ]
        results = list(collection.aggregate(pipeline))
        return {item['_id']: item['latest_result'] for item in results}

    def delete_analysis(self, workspace_id):
        """刪除工作區的所有分析結果"""
        collection = self.db.get_collection('analysis_results')
        return collection.delete_many({'workspace_id': workspace_id})
