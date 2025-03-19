import os
import glob
import requests

#放在backend_refactor-main\service資料夾裡的學校分析功能
class InstitutionAnalysis:
    def analyze(files , start, end, threshold):
        count = 0
        conditionCount = 0
        institution_count = dict()
        publisher_count = dict()
        
        for file in files:
            fileName = file.get('name')
            content = file.get('content')
            institution = ""
            publisher = ""
            insideC1 = False
            insideRP = False
            
            for line in content.split('\n'):
                if line.startswith("TI "):
                    count += 1
                    insideC1 = False
                    insideRP = False
                elif line.startswith("C1 "):
                    insideC1 = True
                    institution += line[3:].strip() + ';'
                elif line.startswith("   ") and insideC1:
                    institution += line[3:].strip() + ';'
                elif line.startswith("RP "):
                    insideRP = True
                    institution += line[3:].strip() + ';'
                elif line.startswith("PU "):
                    publisher = line[3:].strip()
                    if publisher:
                        publisher_count[publisher] = publisher_count.get(publisher, 0) + 1
                elif line.startswith("PY "):
                    year = int(line[3:].strip())
                    if start <= year <= end:
                        if institution:
                            conditionCount += 1
                            institution = institution.strip(';').split(';')
                            for inst in institution:
                                inst = inst.strip()
                                if inst:
                                    institution_count[inst] = institution_count.get(inst, 0) + 1
                    institution = ""
                    insideC1 = False
                    insideRP = False
                else:
                    insideC1 = False
                    insideRP = False
        
        sorted_institutions = sorted(institution_count.items(), key=lambda x: x[1], reverse=True)
        sorted_publishers = sorted(publisher_count.items(), key=lambda x: x[1], reverse=True)
        
        results_institutions = []
        results_publishers = []
        
        for inst in sorted_institutions[:100]:
            if inst[1] < threshold:
                break
            results_institutions.append({
                'institution': inst[0],
                'count': inst[1]
            })
        
        for pub in sorted_publishers[:100]:
            results_publishers.append({
                'publisher': pub[0],
                'count': pub[1]
            })
        
        return count, conditionCount, results_institutions, results_publishers

    def institution_analysis_by_year(files, start, end, threshold):
        school_count = dict()
        
        for file in files:
            content = file.get('content')
            current_year = None  # 用來存放當前處理的年份
            
            for line in content.split('\n'):
                if line.startswith("PY "):
                    current_year = int(line[3:].strip())
                    if not (start <= current_year <= end):
                        current_year = None  # 若年份不符合，重置
                elif (line.startswith("C1 ") or line.startswith("RP ")) and current_year is not None:
                    institutions = [school.strip() for school in line[3:].strip().split(';') if school.strip()]
                    for school in institutions:
                        school_count[school] = school_count.get(school, 0) + 1

        sorted_schools = sorted(school_count.items(), key=lambda x: x[1], reverse=True)
        results_schools = []

        for school in sorted_schools[:100]:
            if school[1] < threshold:
                break
            results_schools.append({
                'school': school[0],
                'count': school[1]
            })

        return results_schools


    

