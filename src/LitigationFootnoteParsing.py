'''
Created on Jun 13, 2012

@author: mchrzanowski
'''

import LitigationFootnoteRegexCollection as LFRC
import nltk
import re
import Utilities


def _check_if_valid_ending(location, hits):
    if _check_if_relevant_section(location, hits):
        return True
    else:
        return False

def _check_if_relevant_section(location, hits):
    
#    print "CHECKING:", hits[location]
    
    # does it contain verbs? detritus usually doesn't.
    contains_verbs = False
    for word in nltk.word_tokenize(hits[location]):
        if re.match("(is|are|hav|has|became|becom|refer|regard|been)", word, re.I):
            contains_verbs = True
            break
    
    if not contains_verbs:
        return False
    
#    print "VERB CHECK PASS"
    
    # now check as to whether we're still in a sentence. 
    # 1). cut everything beforehand into sentences.
    # 2A). if the last paragraph ends in a punk mark, we're good.
    # 2B). if not, it could be detritus like 'table of contents' or something. check everything
    #        past the last real sentence to see whether the words 'see' or 'refer' are there.
    #        These are special words usually indicating that we're still in a given section
    #        but that we're referring to another footnote of the 10-K.
    inside_fragment = False
    
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
            
            for word in punctuated_tokens[end_of_last_sentence_index + 1:]:     # no. check the last sentence fragment. 
                if re.search("(SEE|DISCUSS|REFER|\()", word, re.I):                      # found special word. this is not a complete sentence.
                    inside_fragment = True
                    break
    
    if inside_fragment:
        return False
    
#    print "FRAGMENT CHECK PASS"
    
    # does it contain weird XML/HTML elements? probably not what we want.
    contains_tagging_detritus = False
    for word in nltk.word_tokenize(hits[location]):
        if re.search("(XML$|td$|div$|valign$|falsefalse|[0-9]+px|\/b\/|font-family)", word, re.I):
            contains_tagging_detritus = True
            break
    
    if contains_tagging_detritus:
        return False
    
#    print "JUNK TAG CHECK PASS"
    
    # PASS.
    return True
    
        
def _get_header_of_chunk(location, hits):
    ''' return the header '''
    return nltk.word_tokenize(hits[location])[:5]

def _check_if_valid_header(location, hits):
    
    # header *has* to contain some special keywords.
    contains_keyword = False    
    for word in _get_header_of_chunk(location, hits):
        if re.match("(LITIGATION|CONTINGENC|COMMITMENT|PROCEEDING|LEGAL)", word, re.I):
            contains_keyword = True
            break
    
    if contains_keyword is False:
        return False
    
    
    return True

def _choose_best_hit_for_given_header(current, new):
    
    if Utilities.get_alpha_numeric_count(new) < Utilities.get_alpha_numeric_count(current):
        return new
    
    return current

def _get_all_viable_hits(text):
    
    results = dict()
    
    for regex in LFRC.get_document_parsing_regexes():
        
        hits = re.split(regex, text)
        
        record_text = False
        recorder = []
        
        for i in xrange(len(hits)):
            
            if record_text is False:
                if _check_if_valid_header(i, hits) and _check_if_relevant_section(i, hits):
                    # suck up everything until this section is finished.
                    record_text = True
                    record_header = ''.join(blob for blob in _get_header_of_chunk(i, hits))
                    recorder.append(hits[i - 1])   # assuming this is the token.
                    recorder.append(hits[i])
            
            else:
                if not re.match(regex, hits[i]) and _check_if_valid_ending(i, hits):
                    record_text = False
                    record = ''.join(blob for blob in recorder)
                    
                    if record_header not in results:
                        results[record_header] = record
                    else:
                        results[record_header] = _choose_best_hit_for_given_header(results[record_header], record)
                    
                    recorder = []
                    
                    if _check_if_valid_header(i, hits) and _check_if_relevant_section(i, hits):
                        # suck up everything until this section is finished.
                        record_text = True
                        record_header = ''.join(blob for blob in _get_header_of_chunk(i, hits))
                        recorder.append(hits[i - 1])   # assuming this is the token.
                        recorder.append(hits[i])
                    
                else:
                    recorder.append(hits[i])
        
        if len(recorder) > 0:
            record = ''.join(blob for blob in recorder)
            if record_header not in results:
                results[record_header] = record
            else:
                results[record_header] = _choose_best_hit_for_given_header(results[record_header], record)    
    
#    for result in results:
#        print "NEW:"
#        print results[result]   
        
#    exit(0)

    return [results[key] for key in results]

def get_best_litigation_note_hits(text, cutoff=None):
    if cutoff is not None:
        text = text.split(cutoff)[1]
    return _get_all_viable_hits(text)
    