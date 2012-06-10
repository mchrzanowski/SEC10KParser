'''
Created on Jun 7, 2012

@author: mchrzanowski
'''

import re

def get_relevant_regexes():
    return __default_case_sensitive(),                                                  \
         __default_case_insensitive(),                                                  \
        __item_4_is_skipped_case_insensitive(),                                         \
        __item_4_is_skipped_case_sensitive(),                                           \
        __item_3_is_last_item(),                                                        \
        __item_3_is_lodged_somewhere_case_sensitive(),                                  \
        __item_3_is_lodged_somewhere_case_sensitive_and_item_4_is_skipped(),            \
        __item_3_is_lodged_somewhere_case_sensitive_and_is_last_item_case_sensitive(),  \
        __item_3_is_lodged_somewhere_case_sensitive_no_newlines(),                      \
        __item_3_is_lodged_somewhere_and_item_4_is_skipped_case_sensitive_no_newlines(),\
        __item_3_is_lodged_somewhere_and_is_last_item_case_sensitive_no_newlines(),     \
        __item_3_is_lodged_somewhere_case_insensitive_with_punctuation(),               \
        __item_3_is_lodged_somewhere_and_item_4_is_skipped_case_insensitive_with_punctuation(), \
        __item_3_is_lodged_somewhere_and_is_last_case_insensitive_with_punctuation(),           \
        __item_3_is_lodged_somewhere_case_insensitive_with_punctuation_no_spaces(),             \
        __item_3_is_lodged_somewhere_and_item_4_is_skipped_case_insensitive_with_punctuation_no_spaces(),   \
        __item_3_is_lodged_somewhere_and_is_last_case_insensitive_with_punctuation_no_spaces()
        

def __default_case_sensitive():
    ''' so many 10-Ks have the litigation item structured thusly:
        Item 3. LITIGATION PROCEEDING
            blah blah
        (potential)Item 3A. blah blah
        Item 4. blah blah
        Item 5. blah blah
        
        take advantage of this by using the numbers as well as the fact that 
        the body is between these two Item headers 
    '''
    return re.compile("^\s*ITEM\s*?3\s*[^,].*?(?=^\s*?ITEM\s*?(3A|4))", re.M | re.S), None

def __item_4_is_skipped_case_sensitive():
    return re.compile("^\s*ITEM\s*?3\s*[^,].*?(?=^\s*?ITEM\s*?[5-6])", re.I | re.M | re.S), re.compile("ITEM\s*4", re.I | re.M)

def __item_4_is_skipped_case_insensitive():
    return re.compile("^\s*ITEM\s*?3\s*[^,].*?(?=^\s*?ITEM\s*?[5-6])", re.M | re.S), re.compile("ITEM\s*4", re.I | re.M)

def __default_case_insensitive():
    return re.compile("^\s*ITEM\s*?3\s*[^,].*?(?=^\s*ITEM\s*?(3A|4))", re.I | re.M | re.S), None 

def __try_all_numbers_after_4_and_executive_listing():
    '''
         this regex is slightly different than the default regex: it allows
        for more matching on the Item number. Some 10-Ks miss Item 4 for some reason.
    '''
    return re.compile("^\s*Item\s*?3\s*[^,].*?(?=(Item\s*?[5-6]|EXECUTIVE\s*?OFFICERS))", re.I | re.M | re.S), re.compile("ITEM\s*4", re.I | re.M)

def __item_3_is_last_item():
    '''
        sometimes, item 3 is the last item. after this, what usually follows is a mention
        of the executive committee. so, go from Item 3 to that instead
    '''
    return re.compile("^\s*ITEM\s*?3\s*[^,].*?(?=^\s*?EXECUTIVE\s*?OFFICERS)", re.I | re.M | re.S), re.compile("ITEM\s*4", re.I | re.M)

def __item_3_is_lodged_somewhere_case_sensitive_and_is_last_item_case_sensitive():
    return re.compile("ITEM\s*?3\s*[^,].*?(?=^\s*?EXECUTIVE\s*?OFFICERS)", re.M | re.S), re.compile("ITEM\s*4", re.I | re.M)

def __item_3_is_lodged_somewhere_case_sensitive_and_item_4_is_skipped():
    return re.compile("ITEM\s*?3\s*[^,].*?(?=^\s*?ITEM\s*?[5-6])", re.M | re.S), re.compile("ITEM\s*4", re.I | re.M)
    
def __item_3_is_lodged_somewhere_case_sensitive():
    ''' 
        this one is probably due to my HTML parsing: sometimes, 
        ITEM 3 won't begin at the carriage return. so, attempt to match
        on ITEM 3 somewhere in the text. we assume that item is in all capitals
        to distinguish this from the case of Item 3 being mentioned somewhere else
    '''
    return re.compile("ITEM\s*?3\s*[^,].*?(?=^\s*ITEM\s*?(3A|4))", re.M | re.S), None

def __item_3_is_lodged_somewhere_case_sensitive_no_newlines():
    return re.compile("ITEM\s*?3\s*[^,].*?(?=ITEM\s*?(3A|4))", re.M | re.S), None

def __item_3_is_lodged_somewhere_and_is_last_item_case_sensitive_no_newlines():
    return re.compile("ITEM\s*?3\s*[^,].*?(?=EXECUTIVE\s*?OFFICERS)", re.M | re.S), re.compile("ITEM\s*4", re.I | re.M)

def __item_3_is_lodged_somewhere_and_item_4_is_skipped_case_sensitive_no_newlines():
    return re.compile("ITEM\s*?3\s*[^,].*?(?=ITEM\s*?[5-6])", re.M | re.S), re.compile("ITEM\s*4", re.I | re.M)

def __item_3_is_lodged_somewhere_case_insensitive_with_punctuation():
    ''' similar to item_3_is_lodged_somewhere(), but capitals didn't help us. try to see whether there are multiple
    spaces and punctuation just before the mention of "item 3" '''
    
    return re.compile("(?<=[\.\?\!])\s\s+?ITEM\s*?3\s*[^,].*?(?=ITEM\s*?(3A|4))", re.I | re.M | re.S), None

def __item_3_is_lodged_somewhere_and_item_4_is_skipped_case_insensitive_with_punctuation():
    return re.compile("(?<=[\.\?\!])\s\s+?ITEM\s*?3\s*[^,].*?(?=ITEM\s*?[5-6])", re.I | re.M | re.S), re.compile("ITEM\s*4", re.I | re.M)

def __item_3_is_lodged_somewhere_and_is_last_case_insensitive_with_punctuation():
    return re.compile("(?<=[\.\?\!])\s\s+?ITEM\s*?3\s*[^,].*?(?=EXECUTIVE\s*?OFFICERS)", re.I | re.M | re.S), re.compile("ITEM\s*4", re.I | re.M)

def __item_3_is_lodged_somewhere_case_insensitive_with_punctuation_no_spaces():
    '''
        CIK:0000086144    2012
        Sometimes, the HTML parsing was so horrible that there are no more newlines. This forces my rules to screw up
        as there's little meaningful spacing.
        In this case, remove the restriction that there has to be spaces just before the mention of "item 3"
        but after punctuation.
    '''
    return re.compile("(?<=[\.\?\!])\s*?ITEM\s*?3\s*[^,].*?(?=ITEM\s*?(3A|4))", re.I | re.M | re.S), None

def __item_3_is_lodged_somewhere_and_item_4_is_skipped_case_insensitive_with_punctuation_no_spaces():
    return re.compile("(?<=[\.\?\!])\s*?ITEM\s*?3\s*[^,].*?(?=ITEM\s*?[5-6])", re.I | re.M | re.S), re.compile("ITEM\s*4", re.I | re.M)

def __item_3_is_lodged_somewhere_and_is_last_case_insensitive_with_punctuation_no_spaces():
    return re.compile("(?<=[\.\?\!])\s*?ITEM\s*?3\s*[^,].*?(?=EXECUTIVE\s*?OFFICERS)", re.I | re.M | re.S), re.compile("ITEM\s*4", re.I | re.M)

def is_hit_valid():
    ''' a valid legal proceeding mention - as opposed to something detritus - always has certain words. check for these '''
    return re.compile("(WE|SEE|US|ARE|REFER|APPEAR|REGARD|has|had|is|was|include)", re.I)
