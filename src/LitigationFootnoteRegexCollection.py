'''
Created on Jun 12, 2012

@author: mchrzanowski
'''

import re

def get_document_parsing_regexes():
    return _sections_start_with_word_note_and_are_numbered(), \
        _sections_start_with_word_note_and_are_numbered_more_freeform(), \
        _sections_start_with_word_note_and_are_lettered(), \
        _two_numbers_and_a_period_and_spaces(),    \
        _sections_start_with_an_uppercase_letter(), \
        _two_numbers_and_a_backslash_and_spaces(), \
        _two_numbers_in_parentheses(), \
        _two_numbers_and_a_period_no_spaces(), \
        _two_numbers_and_a_parenthesis_and_spaces(), \
        _two_numbers_and_no_period_with_one_space_with_capitals(), \
        _two_numbers_and_no_period_with_spaces_with_capitals(), \
        _two_numbers_and_a_period_and_spaces_no_pre_numeric_restrictions(), \
        _two_numbers_and_a_period_no_spaces_no_pre_numeric_restrictions(), \
        _whitespace_followed_by_newline_and_a_few_words(), \

def get_cutting_regexes():
    return [re.compile("ITEM\s*?(4|9)\s*(?:A)\s*(?!,).*", re.I | re.M | re.S),    \
    re.compile("P[uU][bB][lL][iI][cC]\s*A[cC]{2}[oO][uU][nN][tT][iI][nN][gG]\s*F[iI][rR][mM].*", re.M | re.S), \
    re.compile("QUARTERLY\s*(\w+\s*){0,5}\s*\(Unaudited.*", re.I | re.M | re.S),
    re.compile("SCHEDULE\s*II.*", re.I | re.M | re.S),   \
    re.compile("(^\s*exhibit[^s].*|^\s*EXHIBIT.*)", re.M | re.S), \
    re.compile("S[iI][gG][nN][aA][tT][uU][rR][eE][sS]?.*", re.M | re.S), \
    re.compile("Executive\s*Officers\s*of\s*the\s*registrant.*", re.I | re.M | re.S), \
    re.compile("The\s*Board\s*of\s*Directors\s*and\s*Stockholders.*", re.I | re.M | re.S), \
    re.compile("REPORT\s*OF\s*MANAGEMENT.*", re.I | re.M | re.S), \
    re.compile("REPORT\s*OF\s*INDEPENDENT\s*AUDITOR.*", re.I | re.M | re.S), \
    re.compile("\.xml.*", re.I | re.M | re.S), \
    re.compile(" XBRL .*", re.I | re.M | re.S), \
    re.compile("REPORT\s*ON\s*INTERNAL\s*CONTROL.*", re.I | re.M | re.S), \
    re.compile("\.gif.*", re.I | re.M | re.S), \
    re.compile("\.htm.*", re.I | re.M | re.S) ]

def get_programming_fragment_check():
    return re.compile("XML|/td|^div$|^valign$|falsefalse|truefalse|falsetrue" + \
                 "|link:[0-9]+px|font-family|link:|background-color|utf-8;" + \
                 "|us-gaap:|px|font", re.I)

def _sections_start_with_an_uppercase_letter():
    return re.compile("((?<![A-Z.])\s[A-Z]\.\s*(?=[A-Z,\.\s:]+))", re.M | re.S)

def _sections_start_with_word_note_and_are_numbered():
    return re.compile("((?<!\()Note\s*[0-9]+(?![0-9,A-Z]))", re.I | re.M | re.S)

def _sections_start_with_word_note_and_are_numbered_more_freeform():
    return re.compile("((?<!\()Note\s*[0-9]+(?![0-9,]))", re.I | re.M | re.S)

def _sections_start_with_word_note_and_are_lettered():
    return re.compile("((?<!\()N[oO][tT][eE]\s*[A-Z])", re.M | re.S)

def _two_numbers_and_a_period_and_spaces():
    return re.compile("((?<![M/0-9])\s+[0-3]?[0-9]\s*\.)", re.I | re.M | re.S)

def _two_numbers_and_a_backslash_and_spaces():
    return re.compile("((?<![M/0-9])\s+[0-3]?[0-9]\s*/)", re.I | re.M | re.S)

def _two_numbers_and_a_period_and_spaces_no_pre_numeric_restrictions():
    return re.compile("((?<![M/])\s+[0-3]?[0-9]\s*\.)", re.I | re.M | re.S)

def _two_numbers_and_a_period_no_spaces_no_pre_numeric_restrictions():
    return re.compile("((?<![M/])\s*[0-3]?[0-9]\s*\.)", re.I | re.M | re.S)

def _two_numbers_in_parentheses():
    return re.compile("(\([0-2]?[0-9]\))", re.M)

def _two_numbers_and_a_period_no_spaces():
    return re.compile("((?<![M/0-9])\s*[0-3]?[0-9]\s*\.)", re.I | re.M | re.S)

def _two_numbers_and_no_period_with_one_space_with_capitals():
    return re.compile("((?<![M/0-9])\s+[0-3]?[0-9]\s(?=[A-Z]))", re.M | re.S)

def _two_numbers_and_no_period_with_spaces_with_capitals():
    return re.compile("((?<![M/0-9])\s+[0-3]?[0-9]\s+(?=[A-Z]))", re.M | re.S)

def _whitespace_followed_by_newline_and_a_few_words():
    return re.compile("(\n^(?!ITEM)(?=(?:\w+\s){1,4}\n))", re.I | re.M | re.S)

def _two_numbers_and_a_parenthesis_and_spaces():
    return re.compile("((?<![M/0-9])\s+[0-3]?[0-9]\s*\)\.?)", re.I | re.M | re.S)
