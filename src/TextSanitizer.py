'''
Created on Jun 7, 2012

@author: mchrzanowski
'''

import re

def sanitize(text):
    ts = TextSanitizer(text)
    ts.clean_text()
    return ts.text

class TextSanitizer(object):
    
    def __init__(self, text):
        self.text = text
        
    def remove_monetary_figures(self, text):
        return re.sub("\$[^\s]+", "dollar", text)
    
    def remove_numbers(self, text):
        return re.sub("[0-9]+", "number", text)
    
    def remove_email_addresses(self, text):
        return re.sub("[^\s]+@[^\s]+", 'emailaddr', text)
    
    def remove_urls(self, text):
        text = re.sub("https?://[^\s]+", 'httpaddr', text)
        text = re.sub("www[^\s]+", "httpaddr", text)
        return text
    
    def clean_text(self):
        self.text = self.remove_email_addresses(self.text)
        self.text = self.remove_monetary_figures(self.text)
        self.text = self.remove_urls(self.text)
        