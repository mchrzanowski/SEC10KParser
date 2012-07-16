'''
Created on Jun 12, 2012

@author: mchrzanowski
'''

import re

def get_document_parsing_regexes():
    return _sections_start_with_word_note_and_are_numbered_case_sensitive(), \
        _sections_start_with_word_note_and_are_numbered(), \
        _sections_start_with_word_note_and_are_numbered_more_freeform(), \
        _note_sections_in_parentheses(), \
        _sections_start_with_word_note_and_are_lettered(), \
        _sections_start_with_word_note_and_are_lettered_no_spaces_with_period(), \
        _two_numbers_and_a_period_and_spaces(),    \
        _sections_start_with_an_uppercase_letter(), \
        _two_numbers_and_a_backslash_and_spaces(), \
        _two_numbers_in_parentheses(), \
        _two_numbers_and_a_period_no_spaces(), \
        _two_numbers_and_a_parenthesis_and_spaces(), \
        _two_numbers_and_no_period_with_one_space_with_capitals(), \
        _two_numbers_and_no_period_with_spaces_with_capitals(), \
        _two_numbers_and_no_period_with_no_spaces_with_capitals(), \
        _two_numbers_and_no_period_with_absolutely_no_spaces_with_capitals(), \
        _two_numbers_and_a_period_and_spaces_no_pre_numeric_restrictions(), \
        _two_numbers_and_a_period_no_spaces_no_pre_numeric_restrictions(), \
        _a_letter_in_parentheses_followed_by_a_cap(), \
        _a_letter_in_parentheses(), \
        _whitespace_followed_by_newline_and_a_few_words(), \
    
def _sections_start_with_an_uppercase_letter():
    return re.compile("((?<![A-Z.])\s[A-Z]\.\s*(?=[A-Z,\.\s:]+))", re.M | re.S)

def _note_sections_in_parentheses():
    return re.compile("(\(\s*Note(?!s)\s*[0-9]+(?![0-9,AB])\)(?!\s*\.))", re.I | re.M | re.S)

def _sections_start_with_word_note_and_are_numbered_case_sensitive():
    return re.compile("((?<!\()NOTE(?!S)\s*[0-9]+(?![0-9,AB])(?!\s*[`'\"])(?:\s*:)?)", re.M | re.S)

def _sections_start_with_word_note_and_are_numbered():
    return re.compile("((?<!\()Note(?!s)\s*[0-9]+(?![0-9,AB])(?!\s*[`'\"])(?:\s*:)?)", re.I | re.M | re.S)

def _sections_start_with_word_note_and_are_numbered_more_freeform():
    return re.compile("((?<!\()Note(?!s)\s*[0-9]+(?![0-9,]))(?!\s*[`'\"])", re.I | re.M | re.S)

def _sections_start_with_word_note_and_are_lettered():
    return re.compile("((?<!\()N[oO][tT][eE]\s+[A-Z])", re.M | re.S)

def _sections_start_with_word_note_and_are_lettered_no_spaces_with_period():
    return re.compile("((?<!\()N[oO][tT][eE]\s*[A-Z]\.)", re.M | re.S)

def _two_numbers_and_a_period_and_spaces():
    return re.compile("((?<![M/0-9])\s+[0-3]?[0-9]\s*\.(?!\s*[0-9]))", re.I | re.M | re.S)

def _two_numbers_and_a_backslash_and_spaces():
    return re.compile("((?<![M/0-9])\s+[0-3]?[0-9]\s*/(?!\s*[0-9]))", re.I | re.M | re.S)

def _two_numbers_and_a_period_and_spaces_no_pre_numeric_restrictions():
    return re.compile("((?<![M/])\s+[0-3]?[0-9]\s*\.(?!\s*[0-9]))", re.I | re.M | re.S)

def _two_numbers_and_a_period_no_spaces_no_pre_numeric_restrictions():
    return re.compile("((?<![M/])\s*[0-3]?[0-9]\s*\.(?!\s*[0-9]))", re.I | re.M | re.S)

def _two_numbers_and_no_period_with_no_spaces_with_capitals():
    return re.compile("((?<![M/0-9])\s+[0-3]?[0-9]\s*(?=[A-Z]))", re.M | re.S)

def _two_numbers_and_no_period_with_absolutely_no_spaces_with_capitals():
    return re.compile("((?<![M/0-9])\s*[0-3]?[0-9]\s*(?=[A-Z]))", re.M | re.S)

def _two_numbers_in_parentheses():
    return re.compile("(\([0-2]?[0-9]\)(?=\s*\.?\s*[A-Z]))", re.M)

def _a_letter_in_parentheses_followed_by_a_cap():
    return re.compile("(\([E-Z]\)\s*(?=[A-Z]))", re.M)

def _a_letter_in_parentheses():
    return re.compile("(\([E-Z]\)(?!\s*[0-9]))", re.M)

def _two_numbers_and_a_period_no_spaces():
    return re.compile("((?<![M/0-9])\s*[0-3]?[0-9]\s*\.(?!\s*[0-9]))", re.I | re.M | re.S)

def _two_numbers_and_no_period_with_one_space_with_capitals():
    return re.compile("((?<![M/0-9])\s+[0-3]?[0-9]\s(?=[A-Z]))", re.M | re.S)

def _two_numbers_and_no_period_with_spaces_with_capitals():
    return re.compile("((?<![M/0-9])\s+[0-3]?[0-9]\s+(?=[A-Z]))", re.M | re.S)

def _whitespace_followed_by_newline_and_a_few_words():
    return re.compile("(\n^(?!ITEM)(?=(?:\w+\s){1,4}\s*\n))", re.I | re.M | re.S)

def _two_numbers_and_a_parenthesis_and_spaces():
    return re.compile("((?<![M/0-9])\s+[0-3]?[0-9]\s*\)\.?(?!\s*[0-9]))", re.I | re.M | re.S)
