'''
Created on Jun 13, 2012

@author: mchrzanowski
'''

from VerbClassifier import VerbClassifier

import LitigationFootnoteRegexCollection as LFRC
import nltk
import re
import Utilities

_word_tokenize_cache = dict()

def _check_if_valid_ending(location, hits):
    #print "CHECKING FOR ENDING:", hits[location], "DONE."
    if _check_whether_section_is_part_of_another_section(location, hits) \
    or _check_whether_header_is_valuable(location, hits):
        #print "NO ENDING"
        return False
    else:
        #print "ENDING."
        return True
    
    
def _check_whether_this_section_is_a_nearby_numeric_section(location, hits, record_footnote_number):
    
    if len(hits[location]) > 1000:
        return False
    
    if record_footnote_number is None:
        return False
    
    new_record_number = _get_footnote_number(location, hits)
    #print "IS IT OVER?", record_footnote_number, hits[location - 1], new_record_number
    
    if new_record_number is None:
        return False
    
    if new_record_number - 2 == record_footnote_number \
    or new_record_number - 1 == record_footnote_number:
        return True
    
    return False

def _get_footnote_number(location, hits):
    number_match = re.search("[0-9]+", ''.join(blob for blob in _get_header_of_chunk(location, hits)), flags=re.M)
    
    if number_match is not None and _contains_numbers(number_match.group(0)):
        return int(number_match.group(0))
    
    return None

_another_section_cache = dict()
def _check_whether_section_is_part_of_another_section(location, hits):
    
    #print "CHECKING TO SEE WHETHER PART OF ANOTHER SECTION", hits[location]
    
    if hits[location] in _another_section_cache:
        punctuated_tokens = _another_section_cache[hits[location]]
    else:
        text_before_slice = ''.join(hit for num, hit in enumerate(hits) if num <= location - 2 and location >= 4 * num // 5)
        # strip everything except those words after the last punctuation mark.
        punctuated_tokens = nltk.punkt.PunktWordTokenizer().tokenize(text_before_slice)
        _another_section_cache[hits[location]] = punctuated_tokens
    
    # check to make sure the last few words don't contain ITEM or NOTE ....
    if re.match("(ITEM|NOTE|Section)", punctuated_tokens[-1], re.I):
        return True
    
    # also, no months!
    if re.match("(Jan((uary)|[^A-Za-z])|Feb((ruary)|[^A-Za-z])|mar((ch)|[^A-Za-z])|apr((il)|[^A-Za-z])|may)", punctuated_tokens[-1], re.I):
        return True
    
    if re.match("(jun((e)|[^A-Za-z])|july|aug((ust)|[^A-Za-z])|sept((ember)|[^A-Za-z])|oct((ober)|[^A-Za-z]))", punctuated_tokens[-1], re.I):
        return True
    
    if re.match("(nov((ember)|[^A-Za-z])|dec((ember)|[^A-Za-z]))", punctuated_tokens[-1], re.I):
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
            for word in punctuated_tokens[end_of_last_sentence_index + 1:]:     # check the last sentence fragment. 

                    # found special word. this is not a complete sentence.
                    # these special words are here because there are all sorts of garbage sections
                    # that have verbs but are actually the text from graphs and charts.
                    if re.search("(SEE|DISCUSS|REFER|describe|SUMMARIZE|disclose|violate|approve)", word, re.I): 
                        #print "MATCH:", word      
                        return True
                
    return False

_verbs = VerbClassifier()
def _does_section_contain_verbs(words):
    
    contains_verbs = False
    for word in words:
        if _verbs.is_word_a_common_verb(word):
            #print "VERB MATCH:", word
            contains_verbs = True
            break
    
    return contains_verbs
    
def _check_whether_chunk_is_new_section(location, hits):
    
    #print "CHECKING:", hits[location]

    if hits[location] in _word_tokenize_cache:
        words_in_hit = _word_tokenize_cache[hits[location]]
    else:
        words_in_hit = nltk.word_tokenize(hits[location])
        _word_tokenize_cache[hits[location]] = words_in_hit
    
    # does it contain verbs? detritus usually doesn't.    
    if not _does_section_contain_verbs(words_in_hit):
        return False
    
    #print "VERB CHECK PASS"
   
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

def _contains_numbers(s):
    
    for char in s:
        if char.isdigit():
            return True
    return False

def _get_header_of_chunk(location, hits):
    ''' return the header '''
    if hits[location] in _word_tokenize_cache:
        return _word_tokenize_cache[hits[location]][:4]
    else:
        words = nltk.word_tokenize(hits[location])
        _word_tokenize_cache[hits[location]] = words
        return words[:4]

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
    
    # we only want subsequent event headers; nothing more.
    if re.search("S[uU][bB][sS][eE][qQ][uU][eE][nN][tT]", compressed_header) \
    and not re.search("Subsequent.*?Event", compressed_header, re.I):
        return False
    
    # first words are never numbers.
    if _contains_numbers(header[0]):
        return False
    
    if len(header) >= 2 and _contains_numbers(header[1]):
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
    
    regexes = [re.compile("ITEM\s*(4|9).*", re.I | re.M | re.S),    \
               re.compile("P[uU][bB][lL][iI][cC]\s*A[cC]{2}[oO][uU][nN][tT][iI][nN][gG]\s*F[iI][rR][mM].*", re.M | re.S), \
               re.compile("QUARTERLY\s*(\w+\s*){0,5}\s*\(Unaudited.*", re.I | re.M | re.S),
               re.compile("SCHEDULE\s*II.*", re.I | re.M | re.S),   \
               re.compile("(^\s*exhibit[^s].*|^\s*EXHIBIT.*)", re.M | re.S), \
               re.compile("S[iI][gG][nN][aA][tT][uU][rR][eE][sS]?.*", re.M | re.S), \
               re.compile("Executive\s*Officers\s*of\s*the\s*registrant.*", re.I | re.M | re.S), \
               re.compile("The\s*Board\s*of\s*Directors\s*and\s*Stockholders.*", re.I | re.M | re.S) ]
    
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
        record_header = None
        recorder = list()
        
        for i in xrange(len(hits)):
            
            # odd-numbered tokens are the things we actually split on
            if i & 1 != 0:
                recorder.append(hits[i])
                continue
            
            if not record_text:
                if _check_whether_header_is_valuable(i, hits) and _check_whether_chunk_is_new_section(i, hits):
                    record_text = True
                    record_header, recorder = _set_up_recorder(i, hits)
                    #record_footnote_number = _get_footnote_number(i - 1, hits)

            else:
                if not re.search(regex, hits[i]) and _check_if_valid_ending(i, hits):
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
                        #record_footnote_number = _get_footnote_number(i - 1, hits)
                    
                else:
                    recorder.append(hits[i])
        
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
    
    return len(results) > 0
        
    
def get_best_litigation_note_hits(text):

    # rip out common places for periods.
    text = re.sub("(?P<lol>(Note|Item)\s*[0-9]+)\s*\.", "\g<lol>", text, flags = re.I | re.M | re.S)
    text = re.sub("(?P<before>[0-9]+)\.(?P<after>[0-9]+)", "\g<before>\g<after>", text, flags=re.I | re.M | re.S)
    text = re.sub("(?P<before>[A-Z][a-z]+)\s+[A-Z]\.\s+(?P<after>[A-Z][a-z]+)", "\g<before>\g<after>", text, flags=re.M | re.S)
    text = re.sub("U\s*\.\s*S\.", "US", text, flags=re.I | re.M | re.S)
    text = re.sub("N\s*\.\s*A\.", "NA", text, flags=re.I | re.M | re.S)
    text = re.sub("K\s*\.\s*K\.", "KK", text, flags=re.I | re.M | re.S)

    # rip out the exhibits
#    chunks = re.split("^\s*EXHIBIT\s*INDEX\s", text, flags=re.I | re.M | re.S)
#    if len(chunks) > 2:
#        text = ''.join(chunks[chunk] for chunk in xrange(len(chunks) - 1))
    
    return _get_all_viable_hits(text)
    