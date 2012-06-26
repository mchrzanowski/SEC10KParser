'''
Created on Jun 25, 2012

@author: mchrzanowski
'''

import os.path
import re
import nltk.stem.porter

class VerbClassifier(object):
    
    PATH_TO_VERB_FILE = os.path.join(os.curdir, '../etc/common_verbs.txt')

    def __init__(self):
        self.verbs = self._get_verbs()
        
    def is_word_a_common_verb(self, word):
        word = word.strip()
        word = word.lower()
        
        if word in self.verbs:
            return True
        
        word = nltk.stem.porter.PorterStemmer().stem_word(word)
        
        if word in self.verbs:
            return True
        
        return False
    
    def _get_verbs(self):
        verbs = set()
        with open(self.PATH_TO_VERB_FILE) as f:
            for line in f:
                verbs.add(line.strip())
        return verbs
