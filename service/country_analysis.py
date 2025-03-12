import os
import glob
import requests

class CountryAnalysis:
    def country_analysis_by_year(files, start, end, threshold):
        count = 0
        conditionCount = 0
        country_count = {}
        
        for file in files:
            content = file.get('content', '')
            country = ""
            insideRP = False
            
            for line in content.split('\n'):
                if line.startswith("TI "):
                    count += 1
                    insideRP = False
                    country = ""
                elif line.startswith("RP "):
                    insideRP = True
                    country += line[3:].strip() + " "
                elif line.startswith("   ") and insideRP:
                    country += line[3:].strip() + " "
                elif line.startswith("PY "):
                    year = int(line[3:].strip())
                    if start <= year <= end and country:
                        conditionCount += 1
                        for entry in country.strip().split(';'):
                            last_part = entry.split(',')[-1].strip()
                            if len(last_part) > 2:
                                country_count[last_part] = country_count.get(last_part, 0) + 1
                    country = ""
                    insideRP = False
                else:
                    insideRP = False
        
        sorted_countries = sorted(country_count.items(), key=lambda x: x[1], reverse=True)
        results = [{"country": c[0], "count": c[1]} for c in sorted_countries if c[1] >= threshold][:100]
        
        return count, conditionCount, results