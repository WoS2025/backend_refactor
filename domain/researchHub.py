import json

class ResearchHub:
    def __init__(self):
        self.papers = []

    def add_paper(self, title, authors, university, location, year, keywords, doi):
        paper = {
            "TI": title,
            "AU": authors,
            "AF": university,
            "SO": location,
            "PY": year,
            "KW": keywords,
            "DI": doi
        }
        self.papers.append(paper)

    def search_by_keyword(self, keyword):
        results = [paper for paper in self.papers if keyword in paper["KW"]]
        return results

    def save_to_file(self, filename):
        with open(filename, 'w', encoding='utf-8') as file:
            json.dump(self.papers, file, ensure_ascii=False, indent=4)

    def load_from_file(self, filename):
        with open(filename, 'r', encoding='utf-8') as file:
            self.papers = json.load(file)


# 使用範例
hub = ResearchHub()

# 添加論文
hub.add_paper("人工智慧在醫學影像分析中的應用", ["李小龍", "王大明"], "上海交通大學", "國際期刊", 2025, ["人工智慧", "醫學影像", "深度學習"], "10.1234/ai.2025.123456")
hub.add_paper("環境保護與可持續發展研究", ["陳美玲", "張志成"], "香港中文大學", "國際會議", 2024, ["環境保護", "可持續發展", "生態學"], "10.5678/env.2024.789012")
hub.add_paper("生物信息學在基因組學中的應用", ["劉華", "趙英"], "北京生命科學研究所", "國內期刊", 2023, ["生物信息學", "基因組學", "大數據"], "10.9012/bio.2023.345678")

# 搜索論文
results = hub.search_by_keyword("人工智慧")
print("搜索結果：")
for paper in results:
    print(paper)

# 保存到文件
hub.save_to_file("research_papers.json")

# 從文件加載
hub.load_from_file("research_papers.json")
print("加載後的論文：")
for paper in hub.papers:
    print(paper)
