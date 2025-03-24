import re

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

    @staticmethod
    def _process_c1(c1_buffer, current_year, year_data):
        c1_content = ' '.join(c1_buffer)
        institutions = re.findall(r'\[.*?\]\s*([^,]+)', c1_content)
        
        if current_year not in year_data:
            year_data[current_year] = {}
            
        for inst in institutions:
            inst = inst.strip()
            if inst:
                year_data[current_year][inst] = year_data[current_year].get(inst, 0) + 1

    def institution_analysis_by_year(files, start, end, threshold):
        year_school_data = {}
        
        for file in files:
            content = file.get('content')
            current_year = None
            c1_buffer = []
            
            for line in content.split('\n'):
                if line.startswith("PY "):
                    current_year = int(line[3:].strip())
                elif line.startswith("C1 "):
                    c1_buffer = [line[3:].strip()]
                elif line.startswith("   ") and c1_buffer:
                    c1_buffer.append(line[3:].strip())
                else:
                    if c1_buffer and current_year and (start <= current_year <= end):
                        InstitutionAnalysis._process_c1(c1_buffer, current_year, year_school_data)
                        c1_buffer = []
            
            if c1_buffer and current_year and (start <= current_year <= end):
                InstitutionAnalysis._process_c1(c1_buffer, current_year, year_school_data)

        # 整理分年數據
        sorted_results = []
        for year in sorted(year_school_data.keys(), reverse=True):
            schools = year_school_data[year]
            filtered = [(k, v) for k, v in schools.items() if v >= threshold]
            sorted_schools = sorted(filtered, key=lambda x: (-x[1], x[0]))[:100]
            if sorted_schools:
                sorted_results.append({
                    'year': year,
                    'schools': [{'school': k, 'count': v} for k, v in sorted_schools]
                })

        return sorted_results