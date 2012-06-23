'''
Created on Jun 13, 2012

@author: mchrzanowski
'''

import LitigationFootnoteRegexCollection as LFRC
import nltk
import re
import Utilities

def _check_if_valid_ending(location, hits):
    if _check_whether_section_is_part_of_another_section(location, hits) or _check_whether_header_is_valuable(location, hits):
        return False
    else:
        return True
    
def _check_whether_section_is_part_of_another_section(location, hits):
    
    # now check as to whether we're still in a sentence. 
    # 1). cut everything beforehand into sentences.
    # 2A). if the last paragraph ends in a punk mark, we're good.
    # 2B). if not, it could be detritus like 'table of contents' or something. check everything
    #        past the last real sentence to see whether the words 'see' or 'refer' are there.
    #        These are special words usually indicating that we're still in a given section
    #        but that we're referring to another footnote of the 10-K.
        
    text_before_slice = ''.join(hit for num, hit in enumerate(hits) if num <= location - 2 and num > location - 12)  # assume the token is hits[location - 1]
    
    # strip everything except those words after the last punctuation mark.
    punctuated_tokens = nltk.punkt.PunktWordTokenizer().tokenize(text_before_slice)
    
    if not re.match("[.?!]", punctuated_tokens[-1][-1]):        # did we end on a normal punct mark?
        
        # no. rewind until we find the last word ending in a punct mark.
        end_of_last_sentence_index = None
        for i in xrange(len(punctuated_tokens) - 1, -1, -1):
            
            if re.match(".*[.?!]$", punctuated_tokens[i]):
                end_of_last_sentence_index = i
                break
        
        # no punct marks at all?! Raise an error; something is screwed up.
        if end_of_last_sentence_index is not None:
#            raise Exception("No punct marks found in:" + ''.join(blob + ' ' for blob in punctuated_tokens))
            #if _does_section_contain_verbs(punctuated_tokens[end_of_last_sentence_index + 1:]):
                for word in punctuated_tokens[end_of_last_sentence_index + 1:]:     # no. check the last sentence fragment. 
                    
                    # found special word. this is not a complete sentence.
                    # these special words are here because there are all sorts of garbage sections
                    # that have verbs but are actually the text from graphs and charts.
                    if re.search("(SEE|DISCUSS|REFER|describe|SUMMARIZE|include|disclose)", word, re.I):       
                        return True
    
    return False

def _does_section_contain_verbs(words):
    
    #print "WORDS:", words
    contains_verbs = False
    for _, pos in nltk.pos_tag(words):  # classify words into parts of speech.
        if re.match("VB[^G]", pos):
            contains_verbs = True
            break
    
    return contains_verbs
    
    
def _check_whether_chunk_is_new_section(location, hits):
    
    #print "CHECKING:", hits[location]

    words_in_hit = nltk.word_tokenize(hits[location])
    
    # does it contain verbs? detritus usually doesn't.    
    if not _does_section_contain_verbs(words_in_hit):
        return False
    
    #print "VERB CHECK PASS"
    
    if _check_whether_section_is_part_of_another_section(location, hits):
        return False
    
    #print "FRAGMENT CHECK PASS"
    
    # does it contain weird XML/HTML elements? probably not what we want.
    for word in words_in_hit:
        if re.search("(XML$|^td$|^div$|^valign$|falsefalse|truefalse|falsetrue|link:[0-9]+px|\/b\/|font-family|xml)", word):
            #print "MATCH:", word
            return False
    
    #print "JUNK TAG CHECK PASS"
    
    return True

        
def _get_header_of_chunk(location, hits):
    ''' return the header '''
    return nltk.word_tokenize(hits[location])[:5]

def _check_whether_header_is_valuable(location, hits):
    
    header = _get_header_of_chunk(location, hits)
    
    # header *has* to contain some special keywords.
    contains_keyword = False    
    for word in header:
        if re.match("(L[iI][tT][iI][gG][aA][tT][iI][oO][nN]|" + \
        "C[oO][nN][tT][iI][nN][gG][eE][nN][cC]|" + \
        "C[oO][mM][mM][iI][tT][mM][eE][nN][tT]|" + \
        "P[rR][oO][cC][eE][eE][dD][iI][nN][gG])", word):
            contains_keyword = True
            #print word, header
            break
    
    if contains_keyword is False:
        return False
    
    return True

def _choose_best_hit_for_given_header(current, new):
    
    if Utilities.get_alpha_numeric_count(new) < Utilities.get_alpha_numeric_count(current):
        return new
    
    return current

def _get_all_viable_hits(text):
    
    def _set_up_recorder(location, hits):
        recorder = list()
        record_header = ''.join(blob for blob in _get_header_of_chunk(i, hits))
        #print "CREATED:", record_header
        recorder.append(hits[i - 1])   # assuming this is the token.
        recorder.append(hits[i])
        return record_header, recorder
        
    results = dict()
    
    for regex in LFRC.get_document_parsing_regexes():
        
        hits = re.split(regex, text)
        
        record_text = False
        recorder = list()
        
        for i in xrange(len(hits)):
            
            if record_text is False:
                if _check_whether_header_is_valuable(i, hits) and _check_whether_chunk_is_new_section(i, hits):
                    record_text = True
                    record_header, recorder = _set_up_recorder(i, hits)

            else:
                if not re.match(regex, hits[i]) and _check_if_valid_ending(i, hits):
                    record_text = False
                    record = ''.join(blob for blob in recorder)
                    
                    if record_header not in results:
                        results[record_header] = record
                    else:
                        results[record_header] = _choose_best_hit_for_given_header(results[record_header], record)
                    
                    recorder = []
                    record_header = None
                    
                    if _check_whether_header_is_valuable(i, hits) and _check_whether_chunk_is_new_section(i, hits):
                        record_text = True
                        record_header, recorder = _set_up_recorder(i, hits)
                    
                else:
                    recorder.append(hits[i])
        
        if len(recorder) > 0 and record_header is not None:
            record = ''.join(blob for blob in recorder)
            if record_header not in results:
                results[record_header] = record
            else:
                results[record_header] = _choose_best_hit_for_given_header(results[record_header], record)  
                
        if len(results) > 0:
            break           # one type of regex is used. only one. notes don't take on different formats within the 10-K.
        
#    for result in results:
#        print "NEW:"
#        print results[result]   
        
#    exit(0)
    return ''.join(results[key] for key in results)
    

def get_best_litigation_note_hits(text, cutoff=None):
    if cutoff is not None:
        text = text.split(cutoff)[1]
    return _get_all_viable_hits(text)
    