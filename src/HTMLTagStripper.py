from HTMLParser import HTMLParser

class HTMLTagStripper(HTMLParser):
    
    def __init__(self):
        self.reset()
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)
    
    @classmethod
    def strip(cls, html):
        s = HTMLTagStripper()
        s.feed(html)
        return s.get_data()