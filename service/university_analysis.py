import re

class InstitutionAnalysis:
    def analyze(files, start, end, threshold):
        total_count = 0
        valid_count = 0
        year_institution_data = {}  # 結構: {年份: {機構: 次數}}
        publisher_count = {}
        
        for file in files:
            content = file.get('content')
            current_year = None
            c1_buffer = []
            
            for line in content.split('\n'):
                # 提取年份
                if line.startswith("PY "):
                    current_year = int(line[3:].strip())
                    total_count += 1
                    if start <= current_year <= end:
                        valid_count += 1
                
                # 處理C1區塊
                elif line.startswith("C1 "):
                    c1_buffer = [line[3:].strip()]
                elif line.startswith("   ") and c1_buffer:
                    c1_buffer.append(line[3:].strip())
                else:
                    if c1_buffer and current_year and (start <= current_year <= end):
                        self._process_c1(c1_buffer, current_year, year_institution_data)
                        c1_buffer = []
                
                # 處理出版社
                if line.startswith("PU ") and current_year and (start <= current_year <= end):
                    publisher = line[3:].strip()
                    if publisher:
                        publisher_count[publisher] = publisher_count.get(publisher, 0) + 1

            # 處理文件末尾的C1殘留
            if c1_buffer and current_year and (start <= current_year <= end):
                self._process_c1(c1_buffer, current_year, year_institution_data)

        # 整理機構數據
        sorted_results = []
        for year in sorted(year_institution_data.keys(), reverse=True):
            institutions = year_institution_data[year]
            filtered = [(k, v) for k, v in institutions.items() if v >= threshold]
            sorted_institutions = sorted(filtered, key=lambda x: (-x[1], x[0]))[:100]
            if sorted_institutions:
                sorted_results.append({
                    'year': year,
                    'institutions': [{'name': k, 'count': v} for k, v in sorted_institutions]
                })

        # 整理出版社數據
        sorted_publishers = sorted(
            publisher_count.items(),
            key=lambda x: (-x[1], x[0])
        )[:100]

        return {
            'total': total_count,
            'valid': valid_count,
            'by_year': sorted_results,
            'publishers': [{'name': k, 'count': v} for k, v in sorted_publishers]
        }

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