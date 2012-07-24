'''
Created on Jul 11, 2012

@author: mchrzanowski
'''

import re

def sanitize_text(text):
    
    text = _edit_text_to_remove_periods(text)
    text = _remove_common_irrelevant_number_patterns(text)
    text = _shape_text(text)
    
    return text

def _shape_text(text):

    text = re.sub("\)(?P<number>[0-9])", ") \g<number>", text)

    return text
    
def _remove_common_irrelevant_number_patterns(text):
    ''' rip out patterns we don't want '''
    
    # years.
    text = re.sub("20[0-7][0-9]", "year", text)
    text = re.sub("19[0-9][0-9]", "year", text)
    
    # months.
    text = re.sub("(?P<month>Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sept?|Oct|Nov|Dec)\s*\.", "\g<month> ", text, flags=re.I | re.M)
    return text

def _edit_text_to_remove_periods(text):
    ''' rip out common places for periods for easier parsing '''

    # periods right after common demarcations
    text = re.sub("(?P<section>(Note|Item)\s*[0-9]+)\s*\.", "\g<section> ", text, flags = re.I | re.M | re.S)
    
    # deal with decimal numbers. do this one several time as sometimes, the whitespace is so bad
    # that the numbers run into each other. each pass removes a few of the decimal points.
    #for _ in xrange(5):
    #    text = re.sub("(?P<before>[0-9]+)\.(?P<after>[0-9]+)", "\g<before>\g<after>", text, flags=re.I | re.M | re.S)
    
    # names with middle initials
    text = re.sub("(?P<before>[A-Z](?!ote)[a-z]+) +[A-Z]\.\s+(?P<after>[A-Z](?!ote)[a-z]+)", "\g<before>\g<after>", text, flags=re.M | re.S)
    
    # common abbreviations with periods.
    text = re.sub("(?P<before>SFAS\s*[0-9]+\s*)\.", "\g<before>", text, flags=re.M) 


    text = re.sub("U\s*\.\s*S\.\s*C\.", "USC", text, flags=re.I | re.M | re.S)
    text = re.sub("B\.\s*S\.\s*C\.", " BSC ", text, flags=re.I | re.M | re.S)
    text = re.sub("S\s*\.\s*E\.\s*C\.", "SEC", text, flags=re.I | re.M | re.S)
    text = re.sub("I\s*\.\s*R\.\s*S\.", "IRS", text, flags=re.I | re.M | re.S)

    text = re.sub("U\s*\.\s*S\.", "US", text, flags=re.I | re.M | re.S)
    text = re.sub("D\s*\.\s*C\.", "DC", text, flags=re.I | re.M | re.S)
    text = re.sub("N\s*\.\s*A\.", "NA", text, flags=re.I | re.M | re.S)
    text = re.sub("K\s*\.\s*K\.", "KK", text, flags=re.I | re.M | re.S)
    text = re.sub("No\.", "No", text, flags=re.M | re.S) 

    text = re.sub("(?P<before>[A-Z])\s*\.(?P<after>[A-Z])\s*\.", "\g<before>\g<after>", text, flags=re.I | re.M | re.S)
    
    return text
