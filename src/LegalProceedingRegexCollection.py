'''
Created on Jun 7, 2012

@author: mchrzanowski
'''

import re

def get_document_parsing_regexes():
    return _default_case_sensitive(),                                                  \
         _default_case_insensitive(),                                                  \
        _item_4_is_skipped_case_insensitive(),                                         \
        _item_4_is_skipped_case_sensitive(),                                           \
        _item_3_is_last_item(),                                                        \
        _item_3_is_lodged_somewhere_case_sensitive(),                                  \
        _item_3_is_lodged_somewhere_case_sensitive_and_item_4_is_skipped(),            \
        _item_3_is_lodged_somewhere_case_sensitive_and_is_last_item_case_sensitive(),  \
        _item_3_is_lodged_somewhere_case_sensitive_no_newlines(),                      \
        _item_3_is_lodged_somewhere_and_item_4_is_skipped_case_sensitive_no_newlines(),\
        _item_3_is_lodged_somewhere_and_is_last_item_case_sensitive_no_newlines(),     \
        _item_3_is_lodged_somewhere_case_insensitive_with_punctuation(),               \
        _item_3_is_lodged_somewhere_and_item_4_is_skipped_case_insensitive_with_punctuation(), \
        _item_3_is_lodged_somewhere_and_is_last_case_insensitive_with_punctuation(),           \
        _item_3_is_lodged_somewhere_case_insensitive_with_punctuation_no_spaces(),             \
        _item_3_is_lodged_somewhere_and_item_4_is_skipped_case_insensitive_with_punctuation_no_spaces(),   \
        _item_3_is_lodged_somewhere_and_is_last_case_insensitive_with_punctuation_no_spaces(),             \
        _item_3_is_lodged_somewhere_assume_legal_proceeding_is_capitalized(),  \
        _item_3_is_lodged_somewhere_assume_item_is_capitalized(),      \
        _item_3_is_just_fine_but_not_item_4_case_insensitive(), \
        _item_3_is_lodged_somewhere_case_insensitive(), \
        _item_3_is_lodged_somewhere_case_insensitive_allow_for_number_packing(),

def _default_case_sensitive():
    ''' so many 10-Ks have the litigation item structured thusly:
        Item 3. LITIGATION PROCEEDING
            blah blah
        (potential)Item 3A. blah blah
        Item 4. blah blah
        Item 5. blah blah
        
        take advantage of this by using the numbers as well as the fact that 
        the body is between these two Item headers 
    '''
    return re.compile("^\s*ITEM\s*?3[^A0-9][.\s]*?[^,].*?(?=^\s*?ITEM\s*?(3A|4))", re.M | re.S), None

def _item_4_is_skipped_case_sensitive():
    return re.compile("^\s*ITEM\s*?3[^A0-9][.\s]*?[^,].*?(?=^\s*?ITEM\s*?[5-6])", re.I | re.M | re.S), re.compile("ITEM\s*4", re.I | re.M)

def _item_4_is_skipped_case_insensitive():
    return re.compile("^\s*ITEM\s*?3[^A0-9][.\s]*?[^,].*?(?=^\s*?ITEM\s*?[5-6])", re.M | re.S), re.compile("ITEM\s*4", re.I | re.M)

def _default_case_insensitive():
    return re.compile("^\s*ITEM\s*?3[^A0-9][.\s]*?[^,].*?(?=^\s*ITEM\s*?(3A|4))", re.I | re.M | re.S), None 

def _try_all_numbers_after_4_and_executive_listing():
    '''
         this regex is slightly different than the default regex: it allows
        for more matching on the Item number. Some 10-Ks miss Item 4 for some reason.
    '''
    return re.compile(  \
        "^\s*[iI][tT][eE][mM]\s*?3[^A0-9][.\s]*?[^,].*?(?=([iI][tT][eE][mM]\s*?[5-6]|E[xX][eE][cC][uU][tT][iI][vV][eE]\s*?O[fF][fF][iI][cC][eE][rR][sS]))", \
        re.M | re.S), re.compile("ITEM\s*4", re.I | re.M)

def _item_3_is_last_item():
    '''
        sometimes, item 3 is the last item. after this, what usually follows is a mention
        of the executive committee. so, go from Item 3 to that instead
    '''
    return re.compile("^\s*[iI][tT][eE][mM]\s*?3[^A0-9][.\s]*?[^,].*?(?=^\s*?E[xX][eE][cC][uU][tT][iI][vV][eE]\s*?O[fF][fF][iI][cC][eE][rR][sS])", re.M | re.S), \
        re.compile("ITEM\s*4", re.I | re.M)

def _item_3_is_lodged_somewhere_case_sensitive_and_is_last_item_case_sensitive():
    return re.compile("ITEM\s*?3[^A0-9][.\s]*?[^,].*?(?=^\s*?E[xX][eE][cC][uU][tT][iI][vV][eE]\s*?O[fF][fF][iI][cC][eE][rR][sS])", re.M | re.S), \
        re.compile("ITEM\s*4", re.I | re.M)

def _item_3_is_lodged_somewhere_case_sensitive_and_item_4_is_skipped():
    return re.compile("ITEM\s*?3[^A0-9][.\s]*?[^,].*?(?=^\s*?ITEM\s*?[5-6])", re.M | re.S), re.compile("ITEM\s*4", re.I | re.M)
    
def _item_3_is_lodged_somewhere_case_sensitive():
    ''' 
        this one is probably due to my HTML parsing: sometimes, 
        ITEM 3 won't begin at the carriage return. so, attempt to match
        on ITEM 3 somewhere in the text. we assume that item is in all capitals
        to distinguish this from the case of Item 3 being mentioned somewhere else
    '''
    return re.compile("ITEM\s*?3[^A0-9][.\s]*?[^,].*?(?=^\s*ITEM\s*?(3A|4|5))", re.M | re.S), None

def _item_3_is_lodged_somewhere_case_sensitive_no_newlines():
    return re.compile("ITEM\s*?3[^A0-9][.\s]*?[^,].*?(?=ITEM\s*?(3A|4|5))", re.M | re.S), None

def _item_3_is_lodged_somewhere_and_is_last_item_case_sensitive_no_newlines():
    return re.compile("ITEM\s*?3[^A0-9][.\s]*?[^,].*?(?=E[xX][eE][cC][uU][tT][iI][vV][eE]\s*?O[fF][fF][iI][cC][eE][rR][sS])", re.M | re.S), \
        re.compile("ITEM\s*4", re.I | re.M)

def _item_3_is_lodged_somewhere_and_item_4_is_skipped_case_sensitive_no_newlines():
    return re.compile("ITEM\s*?3[^A0-9][.\s]*?[^,].*?(?=ITEM\s*?[5-6])", re.M | re.S), re.compile("ITEM\s*4", re.I | re.M)

def _item_3_is_lodged_somewhere_case_insensitive_with_punctuation():
    ''' similar to item_3_is_lodged_somewhere(), but capitals didn't help us. try to see whether there are multiple
    spaces and punctuation just before the mention of "item 3" '''
    
    return re.compile("(?<=[.?!])\s\s+?ITEM\s*?3[^A0-9][.\s]*?[^,].*?(?=ITEM\s*?(3A|4|5))", re.I | re.M | re.S), None

def _item_3_is_lodged_somewhere_and_item_4_is_skipped_case_insensitive_with_punctuation():
    return re.compile("(?<=[.?!])\s\s+?ITEM\s*?3[^A0-9][.\s]*?[^,].*?(?=ITEM\s*?[5-6])", re.I | re.M | re.S), re.compile("ITEM\s*4", re.I | re.M)

def _item_3_is_lodged_somewhere_and_is_last_case_insensitive_with_punctuation():
    return re.compile("(?<=[.?!])\s\s+?[iI][tT][eE][mM]\s*?3[^A0-9][.\s]*?[^,].*?(?=E[xX][eE][cC][uU][tT][iI][vV][eE]\s*?O[fF][fF][iI][cC][eE][rR][sS])", \
                      re.M | re.S), re.compile("ITEM\s*4", re.I | re.M)

def _item_3_is_lodged_somewhere_case_insensitive_with_punctuation_no_spaces():
    '''
        CIK:0000086144    2012
        Sometimes, the HTML parsing was so horrible that there are no more newlines. This forces my rules to screw up
        as there's little meaningful spacing.
        In this case, remove the restriction that there has to be spaces just before the mention of "item 3"
        but after punctuation.
    '''
    return re.compile("(?<=[.?!])\s*?ITEM\s*?3[^A0-9][.\s]*?[^,].*?(?=ITEM\s*?(3A|4|5))", re.I | re.M | re.S), None

def _item_3_is_lodged_somewhere_and_item_4_is_skipped_case_insensitive_with_punctuation_no_spaces():
    return re.compile("(?<=[.?!])\s*?ITEM\s*?3[^A0-9][.\s]*?[^,].*?(?=ITEM\s*?[5-6])", re.I | re.M | re.S), re.compile("ITEM\s*4", re.I | re.M)

def _item_3_is_lodged_somewhere_and_is_last_case_insensitive_with_punctuation_no_spaces():
    return re.compile("(?<=[.?!])\s*?[iI][tT][eE][mM]\s*?3[^A0-9][.\s]*?[^,].*?(?=E[xX][eE][cC][uU][tT][iI][vV][eE]\s*?O[fF][fF][iI][cC][eE][rR][sS])", re.M | re.S), \
        re.compile("ITEM\s*4", re.I | re.M)

def _item_3_is_lodged_somewhere_assume_legal_proceeding_is_capitalized():
    return re.compile("[iI][tT][eE][mM]\s*?3[^A0-9][\s.]*?LEGAL\s*?PROCEEDING.*?(?=[iI][tT][eE][mM]\s*?4)", re.M | re.S), None

def _item_3_is_lodged_somewhere_assume_item_is_capitalized():
    return re.compile("ITEM\s*?3[^A0-9][\s.]*?[lL][eE][gG][aA][lL]\s*?[pP][rR][oO][cC][eE][eE][dD][iI][nN][gG].*?(?=ITEM\s*?(4|5))", re.M | re.S), None

def _item_3_is_just_fine_but_not_item_4_case_insensitive():
    return re.compile("^\s*ITEM\s*?3[^A0-9][.\s]*?[^,].*?(?=\s*?ITEM\s*?(3A|4|5))", re.I | re.M | re.S), None

def _item_3_is_lodged_somewhere_case_insensitive():
    return re.compile("(?<=[A-Z])ITEM\s*?3[^A0-9][.\s]*?[^,].*?(?=\s*?ITEM\s*?(3A|4|5))", re.I | re.M | re.S), None

def _item_3_is_lodged_somewhere_case_insensitive_allow_for_number_packing():
    return re.compile("(?<=[0-9])ITEM\s*?3[^A0-9][.\s]*?[^,].*?(?=\s*?ITEM\s*?(3A|4|5))", re.I | re.M | re.S), \
    re.compile("^\s*ITEM\s*3[\.\s]*Legal\s*Proceedings\s*\(?\s*continued\s*\)?", re.I | re.M)   # make sure to get the whole item proceeding section,
                                                                                                # not a subsection.
def common_words_in_legitimate_legal_proceeding_hits():
    ''' a valid legal proceeding mention - as opposed to something detritus - always has certain words. check for these '''
    return re.compile("(WE$|SEE$|US$|ARE|REFER|APPEAR|REGARD$|has|had|is$|was$|include|none|become|became|will)", re.I)

def good_patterns_and_bad_patterns_in_litigation_proceeding_headers():
    return [re.compile("LEGAL", re.I), re.compile("PROCEEDING", re.I)], [re.compile("PROCEEDINGS?\s*?\)", re.I)]
