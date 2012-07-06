'''
Created on Jun 11, 2012

@author: mchrzanowski
'''

import LegalProceedingRegexCollection as LPRC
import nltk
import re
import Utilities


def _check_whether_chunk_is_new_section(hit):
    ''' 
        a checker to validate whether a given piece of context could
        conceivably be a real litigation mention and not just some detritus 
        picked up by the regexes from the table of contents or something
    '''
    # check to see whether it belongs to the table of contents
    for token in nltk.word_tokenize(hit):
        if re.match(LPRC.common_words_in_legitimate_legal_proceeding_hits(), token):
            return True
        
    return False

def _get_all_possible_hits(text):
    
    ''' 
        Use regexes to match those sections of text that we want. 
        There are several kinds: the pro-regex (meaning do indeed match) and the anti-regex (meaning don't match).
        Both kinds are available for the raw text and then for the header of each hit.
    '''
    results = set()
    
    for regex, anti_regex in LPRC.get_document_parsing_regexes():
                                            
        for hit in re.finditer(regex, text):
            
            candidate = hit.group(0) 
                                        
            if anti_regex is not None and re.search(anti_regex, candidate):
                continue
                                                                                                                                            
            if not _check_whether_chunk_is_new_section(candidate):
                continue
                                        
            # legal proceeding is always mentioned very, very close to the start of the real section
            heading = ''.join(word for word in nltk.word_tokenize(candidate)[:10])
            
            valid_regexes, invalid_regexes = LPRC.good_patterns_and_bad_patterns_in_litigation_proceeding_headers()
            
            valid_regex_pass = True
            invalid_regex_pass = True
                        
            for valid_regex in valid_regexes:
                if not re.search(valid_regex, heading):
                    valid_regex_pass = False
                    break
            
            if valid_regex_pass:
                for invalid_regex in invalid_regexes:
                    if re.search(invalid_regex, heading):
                        invalid_regex_pass = False
                        break
            
            if invalid_regex_pass and invalid_regex:
                results.add(candidate)
                
    return results

def _get_best_result(results):
    ''' get the result with the smallest number of alphanumeric characters '''
    
    min_count = 0
    return_result = None
    
    for result in results:
    
        count = Utilities.get_alpha_numeric_count(result)
        
        if min_count == 0:
            min_count = count
            return_result = result
        
        elif count < min_count:
            min_count = count
            return_result = result
    
    return return_result

def get_best_legal_proceeding_hit(text):
    ''' get all matching results. then select the best one to send back. '''
    results = _get_all_possible_hits(text)
    return _get_best_result(results)
    
    
    