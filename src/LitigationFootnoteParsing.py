'''
Created on Jun 13, 2012

@author: mchrzanowski
'''

from VerbClassifier import VerbClassifier

import LitigationFootnoteRegexCollection as LFRC
import nltk
import re
import Utilities


def _check_if_valid_ending(location, hits):
    #print "CHECKING FOR ENDING:", hits[location]
    if _check_whether_section_is_part_of_another_section(location, hits) or _check_whether_header_is_valuable(location, hits):
        return False
    else:
        return True
    
def _check_whether_section_is_part_of_another_section(location, hits):
    
    #print "CHECKING TO SEE WHETHER PART OF ANOTHER SECTION", hits[location]
    
    # now check as to whether we're still in a sentence. 
    # 1). cut everything beforehand into sentences.
    # 2A). if the last paragraph ends in a punk mark, we're good.
    # 2B). if not, it could be detritus like 'table of contents' or something. check everything
    #        past the last real sentence to see whether the words 'see' or 'refer' are there.
    #        These are special words usually indicating that we're still in a given section
    #        but that we're referring to another footnote of the 10-K.
        
    text_before_slice = ''.join(hit for num, hit in enumerate(hits) if num <= location - 2 and location >= num // 2)  # assume the token is hits[location - 1]
    
    # strip everything except those words after the last punctuation mark.
    punctuated_tokens = nltk.punkt.PunktWordTokenizer().tokenize(text_before_slice)
    
    # check to make sure the last few words don't contain ITEM or NOTE ....
    # also, no months!
    last_previous_word = nltk.word_tokenize(text_before_slice)[-1]
    if re.match("(ITEM|NOTE|Section)", last_previous_word, re.I):
        return True
    
    if re.match("(Jan|Feb|mar|apr|may|jun|july|aug|sept|oct|nov|dec)", last_previous_word, re.I):
        return True
    
    if not re.match("[.?!]", punctuated_tokens[-1][-1]):        # did we end on a normal punct mark?
        
        # no. rewind until we find the last word ending in a punct mark.
        end_of_last_sentence_index = None
        for i in xrange(len(punctuated_tokens) - 1, -1, -1):
            
            if re.match(".*[.?!]$", punctuated_tokens[i]):
                end_of_last_sentence_index = i
                break
        
        #print "LAST FRAGMENT: ", punctuated_tokens[end_of_last_sentence_index + 1:]
        if end_of_last_sentence_index is not None:
#            if _does_section_contain_verbs(punctuated_tokens[end_of_last_sentence_index + 1:]):
            for word in punctuated_tokens[end_of_last_sentence_index + 1:]:     # check the last sentence fragment. 

                    # found special word. this is not a complete sentence.
                    # these special words are here because there are all sorts of garbage sections
                    # that have verbs but are actually the text from graphs and charts.
                    if re.search("(SEE|DISCUSS|REFER|describe|SUMMARIZE|include|disclose|violate|approve)", word, re.I): 
                        #print "MATCH:", word      
                        return True
                
    return False

def _does_section_contain_verbs(words):
    
    contains_verbs = False
    verbs = VerbClassifier()
    for word in words:
        if verbs.is_word_a_common_verb(word):
            #print "VERB MATCH:", word
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
   
    # check to make sure the last few words don't contain ITEM or NOTE ....
    # also, no months!
#    previous_section = nltk.word_tokenize(hits[location - 2])[-1:]
#    for word in previous_section:
#        if re.match("(ITEM|NOTE|Section)", word, re.I):
#            return False
#        if re.match("Jan|Feb|mar|apr|may|jun|july|aug|sept|oct|nov|dec", word, re.I):
#            return False
    
    if _check_whether_section_is_part_of_another_section(location, hits):
        return False
    
    #print "FRAGMENT CHECK PASS"
    
    # does it contain weird XML/HTML elements? probably not what we want.
    for word in words_in_hit:
        if re.search("(XML$|^td$|^div$|^valign$|falsefalse|truefalse|falsetrue|link:[0-9]+px|font-family|xml)", word):
            #print "MATCH:", word
            return False
    
    #print "JUNK TAG CHECK PASS"
    
    return True


def _is_number(s):
    s = re.sub(",", "", s)
    s = re.sub("/", "", s)
    try:
        float(s)
        return True
    except ValueError:
        return False

def _get_header_of_chunk(location, hits):
    ''' return the header '''
    return nltk.word_tokenize(hits[location])[:4]

def _check_whether_header_is_valuable(location, hits):
    
    header = _get_header_of_chunk(location, hits)
    
    #print "CHECKING HEADER:", header
    
    # header *has* to contain some special keywords.
    contains_keyword = False    
    for word in header:
        if re.match("(L[iI][tT][iI][gG][aA][tT][iI][oO][nN]|" + \
        "C[oO][nN][tT][iI][nN][gG][eE][nN][cC]|" + \
        "C[oO][mM][mM][iI][tT][mM][eE][nN][tT]|" + \
        "P[rR][oO][cC][eE][eE][dD][iI][nN][gG]|" + \
        "C[oO][nN][tT][iI][gG][eE][nN][cC][iI][eE][sS]|" + \
        "L[eE][gG][aA][lL]|" +
        "S[uU][bB][sS][eE][qQ][uU][eE][nN][tT])", word):
            contains_keyword = True
            #print word, header
            break
    
    if not contains_keyword:
        return False

    # now check for common bigrams that we don't want.
    compressed_header = ''.join(word for word in header)
    
    if re.search("LEASE\s*COMMITMENT", compressed_header, re.I | re.M | re.S)   \
    or re.search("ENERGY\s*COMMITMENT", compressed_header, re.I | re.M | re.S)  \
    or re.search("Indemnity", compressed_header, re.I | re.M | re.S)    \
    or re.search("Legal\s*Fees", compressed_header, re.I | re.M | re.S) \
    or re.search("Reimbursement", compressed_header, re.I | re.M | re.S) \
    or re.search("Assistance.*Litigation", compressed_header, re.I | re.M | re.S):
        return False
    
    # first words are never numbers.
    if _is_number(header[0]):
        return False
    
    if len(header) >= 2 and _is_number(header[1]):
        return False
    
    return True

def _choose_best_hit_for_given_header(current, new):
    
    if Utilities.get_alpha_numeric_count(new) < Utilities.get_alpha_numeric_count(current):
        return new
    
    return current

def _subsequent_event_text_handler(text):
    
    # check to see whether the text mentions litigation:
    if not re.search('(litigation|legal)', text, re.I):
        return ''
    
    return text

def _cut_text_if_needed(text):
    
    
    # text might be too long because this is the last
    # legal footnote. so cut it along markers that would
    # not be OK to cut on normally.
    
    regexes = [re.compile("ITEM\s*9.*", re.I | re.M | re.S),    \
               re.compile("P[uU][bB][lL][iI][cC]\s*A[cC]{2}[oO][uU][nN][tT][iI][nN][gG]\s*F[iI][rR][mM].*", re.M | re.S), \
               re.compile("QUARTERLY\s*(\w+\s*){0,5}\s*\(Unaudited.*", re.I | re.M | re.S),
               re.compile("SCHEDULE\s*II.*", re.I | re.M | re.S),   \
               re.compile("(^\s*exhibit[^s].*|^\s*EXHIBIT.*)", re.M | re.S), \
               re.compile("S[iI][gG][nN][aA][tT][uU][rR][eE][sS]?.*", re.M | re.S)]
    
    for regex in regexes:
        if re.search(regex, text):
            text = re.sub(regex, "", text)
        
    return text
    

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
        
        #print "NEW regex:", regex.pattern
        
        hits = re.split(regex, text)
        
        record_text = False
        recorder = list()
        
        for i in xrange(len(hits)):
            
            if not record_text:
                if _check_whether_header_is_valuable(i, hits) and _check_whether_chunk_is_new_section(i, hits):
                    record_text = True
                    record_header, recorder = _set_up_recorder(i, hits)

            else:
                if not re.match(regex, hits[i]) and _check_if_valid_ending(i, hits):
                    record_text = False
                    record = ''.join(blob for blob in recorder)
                        
                    record = _cut_text_if_needed(record)
                    
                    if re.search("SUBSEQUENT", record_header, re.I):
                        record = _subsequent_event_text_handler(record)
                    
                    if record_header not in results:
                        results[record_header] = record
                    else:
                        results[record_header] = _choose_best_hit_for_given_header(results[record_header], record)
                    
                    recorder = list()
                    record_header = None
                    
                    if _check_whether_header_is_valuable(i, hits) and _check_whether_chunk_is_new_section(i, hits):
                        record_text = True
                        record_header, recorder = _set_up_recorder(i, hits)
                    
                else:
                    recorder.append(hits[i])
                    #print "APPENDED:", hits[i]
        
        if len(recorder) > 0 and record_header is not None:
            
            record = ''.join(blob for blob in recorder)
                        
            record = _cut_text_if_needed(record)
            
            if re.search("SUBSEQUENT", record_header, re.I):
                record = _subsequent_event_text_handler(record)
            
            if record_header not in results:
                results[record_header] = record
            else:
                results[record_header] = _choose_best_hit_for_given_header(results[record_header], record)  
                
        if _are_results_from_this_regex_split_acceptable(results):
            break           # one type of regex is used. only one. notes don't take on different formats within the 10-K.

    return ''.join(results[key] + '\n\n' for key in results)

def _are_results_from_this_regex_split_acceptable(results):
    '''# do one of the headers mention "CONTINGENCY" or "COMMITMENT" ? 
    # results *almost always* do
    
    for header in results:
        if re.search("COMMITMENT", header, re.I) \
        or re.search("CONTINGENC", header, re.I):
            return True
        
    # next, check the actual text. maybe it's there?
    for header in results:
        if re.search("COMMITMENT", results[header], re.I) \
        or re.search("CONTINGENC", header, re.I):
            return True
    
    return False
    '''
    return len(results) > 0
        
    
def get_best_litigation_note_hits(text):

    # rip out common places for periods.
    text = re.sub("(?P<lol>(Note|Item)\s*[0-9]+)\s*\.", "\g<lol>", text, flags = re.I | re.M | re.S)
    text = re.sub("(?P<before>[0-9]+)\.(?P<after>[0-9]+)", "\g<before>\g<after>", text, flags=re.I | re.M | re.S)
    
    # rip out the exhibits
    chunks = re.split("^\s*EXHIBIT\s*INDEX\s", text, flags=re.I | re.M | re.S)
    if len(chunks) > 2:
        text = ''.join(chunks[chunk] for chunk in xrange(len(chunks) - 1))
    
    return _get_all_viable_hits(text)
    