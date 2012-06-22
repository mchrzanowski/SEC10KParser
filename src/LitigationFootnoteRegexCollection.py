'''
Created on Jun 12, 2012

@author: mchrzanowski
'''

import re

def get_document_parsing_regexes():
    return properly_formatted_note_sections_case_insensitive(), \

def properly_formatted_note_sections_case_insensitive():
    return re.compile("(Note\s*[0-9]+)", re.I | re.M | re.S)