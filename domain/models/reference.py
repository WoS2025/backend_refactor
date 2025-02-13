class reference:
    def __init__(self, name, url):
        self.name = name
        self.url = url
    
    def to_dict(self):
        return {
            'name': self.name,
            'url': self.url
        }
        