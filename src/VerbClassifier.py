'''
Created on Jun 25, 2012

@author: mchrzanowski
'''

import os.path
import re

class VerbClassifier(object):
    
    PATH_TO_VERB_FILE = os.path.join(os.curdir, '../etc/common_verbs.txt')

    def __init__(self):
        self.verbs = self._get_verbs()
        
    def is_word_a_common_verb(self, word):
        word = word.strip()
        
        if word in self.verbs:
            return True
        
        for verb in self.verbs:
            
            # match assuming there's a suffix
            if re.search(verb + "ed$", word, re.I) or   \
            re.search(verb + "d$", word, re.I) or       \
            re.search(verb + "ing$", word, re.I) or     \
            re.search(verb + "s$", word, re.I):
                print verb, word
                return True
        
        return False
    
    def _get_verbs(self):
        verbs = set()
        with open(self.PATH_TO_VERB_FILE) as f:
            for line in f:
                verbs.add(line.strip())
        return verbs
