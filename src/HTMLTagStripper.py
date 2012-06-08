'''
Created on Jun 8, 2012

@author: mchrzanowski
'''

from HTMLParser import HTMLParser

class HTMLTagStripper(HTMLParser):
    ''' 
        simple class to strip all HTML from some text.
        example derived from:
        http://stackoverflow.com/questions/753052/strip-html-from-strings-in-python
    '''
    
    def __init__(self):
        self.reset()
        self.fed = []
        
    def handle_data(self, d):
        self.fed.append(d)
        
    def get_data(self):
        return ''.join(self.fed)
    
    @staticmethod
    def strip(html):
        s = HTMLTagStripper()
        s.feed(html)
        return s.get_data()
