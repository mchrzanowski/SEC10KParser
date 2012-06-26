'''
Created on Jun 12, 2012

@author: mchrzanowski
'''

import re

def get_document_parsing_regexes():
    return numbered_and_classified_footnotes(), \
        well_formatted_numbered_footnotes_excluding_years()

def numbered_and_classified_footnotes():
    return re.compile("(Note\s*[0-9]+)", re.I | re.M | re.S)

def well_formatted_numbered_footnotes_excluding_years():
    return re.compile("((?<!ITEM)\s+[0-9]{1,2}\.\s*)", re.I | re.M | re.S)