'''
Created on Jun 12, 2012

@author: mchrzanowski
'''

import re

def get_document_parsing_regexes():
    return _sections_start_with_word_note(), \
        _two_numbers_and_a_period_and_spaces(),    \
        _two_numbers_and_a_backslash_and_spaces(), \
        _two_numbers_in_parentheses(), \
        _two_numbers_and_a_period_no_spaces(), \
        _whitespace_followed_by_newline_and_a_few_words()

def _sections_start_with_word_note():
    return re.compile("(Note\s*[0-9]+)", re.I | re.M | re.S)

def _two_numbers_and_a_period_and_spaces():
    return re.compile("((?<!ITEM)\s+[0-2]?[0-9]\s*\.)", re.I | re.M | re.S)

def _two_numbers_and_a_backslash_and_spaces():
    return re.compile("((?<!ITEM)\s+[0-2]?[0-9]\s*/)", re.I | re.M | re.S)

def _two_numbers_in_parentheses():
    return re.compile("(\([0-2]?[0-9]\))", re.M)

def _two_numbers_and_a_period_no_spaces():
    return re.compile("((?<!ITEM)(\s*)[0-2]?[0-9]\s*\.)", re.I | re.M | re.S)

def _whitespace_followed_by_newline_and_a_few_words():
    return re.compile("(\n+^(?!ITEM)(?=(\w+\s){1,4}\n))", re.I | re.M | re.S)
