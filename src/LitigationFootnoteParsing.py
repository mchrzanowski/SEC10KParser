'''
Created on Jun 13, 2012

@author: mchrzanowski
'''

import LitigationFootnoteRegexCollection as LFRC
import nltk
import re

def _check_if_valid_ending(location, hits):
    return True
    #

def _check_if_valid_hit(location, hits):
    
    # does it contain verbs?
    contains_verbs = False
    for word in nltk.word_tokenize(hits[location]):
        if re.match("(is|are|hav|became|becom|refer|regard)", word, re.I):
            contains_verbs = True
            break
    
    if contains_verbs:
        return True
    else:
        return False
    
'''    # check whether we're in a sentence fragment. if so, return False.
    if location >= 2:
        
        text_before_slice = hits[location - 2].strip()  # assume the token is hits[location - 1]
        
        if re.match("(\.|\?|\!)", text_before_slice[-1]):
            return True
    
    return False
'''        
        
def _check_if_valid_header(location, hits):
    
    # header *has* to contain some special keywords.
    start_of_text = nltk.word_tokenize(hits[location])[:5]
    
    for word in start_of_text:
        
        if re.match("(LITIGATION|CONTINGENC|COMMITMENT)", word, re.I):
            return True
    
    return False        

def _get_all_viable_hits(text):
    
    results = []
    
    for regex in LFRC.get_document_parsing_regexes():
        
        hits = re.split(regex, text)
        
        record_text = False
        recording = []
        for i in xrange(len(hits)):
            
            if record_text is False:
                if _check_if_valid_header(i, hits) and _check_if_valid_hit(i, hits):
                    # suck up everything until this section is finished.
                    record_text = True
                    recording.append(hits[i - 1])   # assuming this is the header.
                    recording.append(hits[i])
            
            else:
                if _check_if_valid_ending(i, hits):
                    record_text = False
                    results.append(''.join(blob for blob in recording))
                    recording = []
                
                else:
                    recording.append(hits[i])
        
        if len(recording) > 0:
            results.append(''.join(blob for blob in recording))
    
    for result in results:
        print "NEW:"
        print result    

def get_best_litigation_note_hits(text, cutoff=None):
    if cutoff is not None:
        text = text.split(cutoff)[1]
    results = _get_all_viable_hits(text)
    