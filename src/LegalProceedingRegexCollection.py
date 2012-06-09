'''
Created on Jun 7, 2012

@author: mchrzanowski
'''

import re

def get_relevant_regexes():
    return __default(), __item_3_is_lodged_somewhere(), __item_3_is_lodged_somewhere_with_no_capitals(),    \
        __item_3_is_lodged_somewhere_with_no_capitals_and_no_newlines(), __try_all_numbers_after_4_and_executive_listing()

def __default():
    ''' so many 10-Ks have the litigation item structured thusly:
        Item 3. LITIGATION PROCEEDING
            blah blah
        (potential)Item 3A. blah blah
        Item 4. blah blah
        Item 5. blah blah
        
        take advantage of this by using the numbers as well as the fact that 
        the body is between these two Item headers 
    '''
        
    return "^\s*Item\s*?3.*?(?=\n\s*Item\s*?(3A|4)[^0-9])", re.I | re.M | re.S

def __try_all_numbers_after_4_and_executive_listing():
    '''
         this regex is slightly different than the default regex: it allows
        for more matching on the Item number. Some 10-Ks miss Item 4 for some reason.
    '''
    return "^\s*Item\s*?3.*?(?=(Item\s*?[5-6]|EXECUTIVE.*?OFFICERS?))", re.I | re.M | re.S

def __item_3_is_last_item():
    '''
        sometimes, item 3 is the last item. after this, what usually follows is a mention
        of the executive committee. so, go from Item 3 to that instead
    '''
    return "^\s*Item\s*?3.*?.*?(?=EXECUTIVE.*?OFFICERS?)", re.I | re.M | re.S
    

def __item_3_is_lodged_somewhere():
    ''' 
        this one is probably due to my HTML parsing: sometimes, 
        ITEM 3 won't begin at the carriage return. so, attempt to match
        on ITEM 3 somewhere in the text. we assume that item is in all capitals
        to distinguish this from the case of Item 3 being mentioned somewhere else
    '''
    return "ITEM\s*?3.*?(?=ITEM\s*?(3A|4)[^0-9])", re.M | re.S


def __item_3_is_lodged_somewhere_with_no_capitals():
    ''' similar to item_3_is_lodged_somewhere(), but capitals didn't help us. try to see whether there are multiple
    spaces and punctuation just before the mention of "item 3" '''
    
    return "(?<=[\.\?\!]\s)\s+?ITEM\s*?3.*?(?=ITEM\s*?(3A|4)[^0-9])", re.I | re.M | re.S

def __item_3_is_lodged_somewhere_with_no_capitals_and_no_newlines():
    '''
        CIK:0000086144    2012
        Sometimes, the HTML parsing was so horrible that there are no more newlines. This forces my rules to screw up
        as there's little meaningful spacing.
        In this case, remove the restriction that there has to be spaces just before the mention of "item 3"
        but after punctuation.
    '''
    return "(?<=[\.\?\!])\s*ITEM\s*?3.*?(?=ITEM\s*?(3A|4)[^0-9])", re.I | re.M | re.S


    