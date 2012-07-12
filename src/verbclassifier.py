'''
Created on Jun 25, 2012

@author: mchrzanowski
'''

import Constants
import re
import nltk.stem.porter

    
_verbs = set()
       
def is_word_a_common_verb(word):
    word = word.strip()
    word = word.lower()
    
    if len(_verbs) == 0:
        _populate_cache()
    
    if word in _verbs:
        return True
    
    word = nltk.stem.porter.PorterStemmer().stem_word(word)
    
    if word in _verbs:
        return True
    
    return False
    
def _populate_cache():
    with open(Constants.PATH_TO_VERB_FILE) as f:
        for line in f:
            if Constants.FLAG_INDICATING_VERB_SHOULD_BE_SKIPPED not in line:
                _verbs.add(line.strip())
