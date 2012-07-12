'''
Created on Jul 11, 2012

@author: mchrzanowski
'''

import nltk
import re

_last_sentence_fragment_as_list_cache = dict()
_last_sentence_fragment_as_string_cache = dict()
_punctuated_section_cache = dict()
_word_tokenize_cache = dict()

def word_tokenize_hit(location, hits):
    if hits[location] not in _word_tokenize_cache:
        words = nltk.word_tokenize(hits[location])
        _word_tokenize_cache[hits[location]] = words
          
    return _word_tokenize_cache[hits[location]]


def punctuate_prior_section(location, hits):
    if hits[location] not in _punctuated_section_cache:
        text_before_slice = ''.join(hit for num, hit in enumerate(hits) if num <= location - 2 and location >= 6 * num // 7)
        punctuated_tokens = nltk.punkt.PunktWordTokenizer().tokenize(text_before_slice)
        _punctuated_section_cache[hits[location]] = punctuated_tokens
        
    return _punctuated_section_cache[hits[location]]


def get_last_sentence_fragment(location, hits, return_as_string=False):
    ''' rewind until we find the last word ending in a punct mark.
    return this fragment (might not be a full sentence) as a string or a list '''
    
    if hits[location] not in _last_sentence_fragment_as_list_cache:
        
        punctuated_tokens = punctuate_prior_section(location, hits)
        
        if re.match("[.?!]", punctuated_tokens[-1][-1]):
             _last_sentence_fragment_as_list_cache[hits[location]] = None
        
        else:
            end_of_last_sentence_index = None
            for i in xrange(len(punctuated_tokens) - 1, -1, -1):
            
                if re.search("[.?!]", punctuated_tokens[i]):
                    end_of_last_sentence_index = i
                    new_token_sans_punct = re.sub(".*[.?!]", "", punctuated_tokens[i], flags=re.M | re.S)
                    punctuated_tokens.insert(i + 1, new_token_sans_punct)
                    break
            
            if end_of_last_sentence_index is not None:
                _last_sentence_fragment_as_list_cache[hits[location]] = punctuated_tokens[end_of_last_sentence_index + 1:]
            else:
                 _last_sentence_fragment_as_list_cache[hits[location]] = None

    if not return_as_string:
        return _last_sentence_fragment_as_list_cache[hits[location]]
    
    if hits[location] not in _last_sentence_fragment_as_string_cache:
        
        if _last_sentence_fragment_as_list_cache[hits[location]] is None:
            _last_sentence_fragment_as_string_cache[hits[location]] = ''
        
        else:
            joined_fragment = ''.join(_last_sentence_fragment_as_list_cache[hits[location]])
            _last_sentence_fragment_as_string_cache[hits[location]] = joined_fragment
        
    return _last_sentence_fragment_as_string_cache[hits[location]]
    
