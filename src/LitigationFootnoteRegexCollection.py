'''
Created on Jun 12, 2012

@author: mchrzanowski
'''

import re

def get_document_parsing_regexes():
    return _sections_start_with_word_note(), \
        _two_numbers_and_a_period(),    \
        _two_numbers_and_a_backslash()

def _sections_start_with_word_note():
    return re.compile("(Note\s*[0-9]+)", re.I | re.M | re.S)

def _two_numbers_and_a_period():
    return re.compile("((?<!ITEM)\s+[0-9]{1,2}\.[^0-9])", re.I | re.M | re.S)

def _two_numbers_and_a_backslash():
    return re.compile("((?<!ITEM)\s+[0-9]{1,2}/[^0-9])", re.I | re.M | re.S)