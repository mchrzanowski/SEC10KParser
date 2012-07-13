'''
Created on Jul 11, 2012

@author: mchrzanowski
'''

import litigationfootnoteparsing as lfp
import nltk
import re
import Utilities

def get_header_of_chunk(location, hits):
    ''' return the header. 
    defined as being the first 4 alphanumeric blobs of a section '''
    words = lfp.wordtokencreation.word_tokenize_hit(location, hits)
    
    return_list = list()
    for piece in words:
        if re.search("[()A-Z0-9a-z]", piece):
            return_list.append(piece)
        
        if len(return_list) == 4:
            break
    
    return return_list

def check_whether_header_is_valuable(location, hits):
    
    header = get_header_of_chunk(location, hits)
    
    #print "CHECKING HEADER:", header
    
    # header *has* to contain some special keywords.
    contains_keyword = False    
    for word in header:
        if re.match(lfp.headerpatternrepository.get_pattern_of_headers_we_want(), word):
            contains_keyword = True
            #print word, header
            break
    
    if not contains_keyword:
        return False

    # now check for common bigrams that we don't want.
    compressed_header = ''.join(header)
    
    #print header
    #print compressed_header
    
    # debt or other by themselves are not useful.
    if re.search("D[eE][bB][tT]|O[tT][hH][eE][rR]", compressed_header) \
    and not re.search("Litigation|Contingenc|Commitment|Proceeding|" + \
                      "Contigencies|Legal|Subsequent", compressed_header, re.I):
        return False
    
    for regex in lfp.headerpatternrepository.get_patterns_of_headers_we_dont_want():
        if re.search(regex, compressed_header):
            return False
    
    # we only want subsequent event headers; nothing more.
    if re.search("S[uU][bB][sS][eE][qQ][uU][eE][nN][tT]", compressed_header) \
    and not re.search("Subsequent.*?Event", compressed_header, re.I):
        return False
    
    # first words are never numbers.
    if Utilities.contains_numbers(header[0]) \
    or (len(header) >= 2 and Utilities.contains_numbers(header[1])):
        #print "MATCH ON NUMBER"
        return False
    
    # does it have a letter in parentheses that is not "A"? 
    # if so, forget it.
    if re.search("\([B-Zb-z]\)", compressed_header):
        return False
    
    return True
