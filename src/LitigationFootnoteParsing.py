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
    if _check_whether_section_is_part_of_another_section(location, hits) \
    or _check_whether_header_is_valuable(location, hits):
        return False
    else:
        return True

_another_section_cache = dict()
def _check_whether_section_is_part_of_another_section(location, hits):
    
    #print "CHECKING TO SEE WHETHER PART OF ANOTHER SECTION", hits[location]
    
    if hits[location] in _another_section_cache:
        punctuated_tokens = _another_section_cache[hits[location]]
    else:
        text_before_slice = ''.join(hit for num, hit in enumerate(hits) if num <= location - 2 and location >= 5 * num // 6)
        # strip everything except those words after the last punctuation mark.
        punctuated_tokens = nltk.punkt.PunktWordTokenizer().tokenize(text_before_slice)
        _another_section_cache[hits[location]] = punctuated_tokens
    
    # check to make sure the last few words don't contain common words 
    # that have numbers after them.
    if re.match("ITEM|NOTE|Section|region|division|unit|units", punctuated_tokens[-1], re.I):
        #print 'MATCH ON end word regex'
        return True
    
    # also, no months!
    if re.match("(Jan((uary)|[^A-Za-z])|Feb((ruary)|[^A-Za-z])|mar((ch)|[^A-Za-z])|apr((il)|[^A-Za-z])|may)", punctuated_tokens[-1], re.I):
        #print 'MATCH ON MONTH1'
        return True
    
    if re.match("(jun((e)|[^A-Za-z])|july|aug((ust)|[^A-Za-z])|sept((ember)|[^A-Za-z])|oct((ober)|[^A-Za-z]))", punctuated_tokens[-1], re.I):
        #print 'MATCH ON MONTH2'
        return True
    
    if re.match("(nov((ember)|[^A-Za-z])|dec((ember)|[^A-Za-z]))", punctuated_tokens[-1], re.I):
        #print 'MATCH ON MONTH3'
        return True
    
    if not re.match("[.?!]", punctuated_tokens[-1][-1]):        # did we end on a normal punct mark?
        
        # no. rewind until we find the last word ending in a punct mark.
        end_of_last_sentence_index = None
        for i in xrange(len(punctuated_tokens) - 1, -1, -1):
            
            if re.search("[.?!]", punctuated_tokens[i]):
                end_of_last_sentence_index = i
                new_token_sans_punct = re.sub(".*[.?!]", "", punctuated_tokens[i], flags=re.M | re.S)
                punctuated_tokens.insert(i + 1, new_token_sans_punct)
                break
        
        #print "LAST FRAGMENT: ", punctuated_tokens[end_of_last_sentence_index + 1:]
        if end_of_last_sentence_index is not None:
            
            compressed_fragment = ''.join(blob for blob in punctuated_tokens[end_of_last_sentence_index + 1:])
            
            # everything is contained in parentheses? probably OK.
            if re.search("^\(.*\)$", compressed_fragment, flags=re.M | re.S):
                #print 'MATCH on parens end'
                return False
                
            # common terms with numbers after them.
            if re.search("Units?\s*[0-9]*$", compressed_fragment) \
            or re.search("Region\s*[0-9]*$", compressed_fragment) \
            or re.search("USC\s*[0-9]*$", compressed_fragment):
                #print "MATCH on end words with numbers attached."
                return True
            
            left_parens, right_parens = Utilities.count_parentheses(compressed_fragment)
            
            if left_parens > right_parens:
                return True
            
            found_special_word_that_might_be_from_a_table = False                
            
            for word in punctuated_tokens[end_of_last_sentence_index + 1:]:     # check the last sentence fragment. 

                # found special word. this is not a complete sentence.
                # these special words are here because there are all sorts of garbage sections
                # that have verbs but are actually the text from graphs and charts.
                if re.search("see|under|SUMMARIZEd|included|DISCUSS|REFER|describe|disclose|violate|approve", word, re.I): 
                    #print "MATCH:", word
                    found_special_word_that_might_be_from_a_table = True
                    break

            if found_special_word_that_might_be_from_a_table:
                    
                # now, do additional checks to see whether we picked up a table. 
                # tables normally have units of currency as well as the word follows somewhere.
                # if these hold, then we're probably in a table from a previous section and we can 
                # safely start a new section.
                if re.search("(in)?\s*(millions|thousands|billions)", compressed_fragment, re.I | re.M | re.S) \
                and re.search("total|follows", compressed_fragment, re.I | re.M | re.S):
                    #print "MATCH ON currency"
                    #print 'MATCH ON FOLLOWS|total'
                    return False
                    
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
    
    # does it contain weird XML/HTML elements in the top-most section? 
    # probably not what we want.
    
    top_section = ''.join(blob for blob in re.split("\n\n+", hits[location])[:3])
    
    #print "FIRST:" + top_section + "DONE"
    
    if re.search(LFRC.get_programming_fragment_check(), top_section):
        return False
    
    #print "JUNK TAG CHECK PASS"
    
    # does it contain the phrase "this Amendment"? If so, it's probably not what we want.
    if re.search("this\s*Amendment", hits[location][:len(hits[location]) // 4]):
        #print "FAIL ON Amendment check"
        return False
    
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
        "C[oO][nN][tT][iI][nN][gG][eE][nN][tTcC]|" + \
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
    
    for regex in LFRC.get_names_of_headers_we_dont_want():
        if re.search(regex, compressed_header):
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
    
#    if re.search('`', compressed_header) \
#    or re.search('"', compressed_header):
#        return False
    
    return True

def _subsequent_event_text_handler(text):
    
    # check to see whether the text mentions litigation:
    if not re.search('(litigation|legal)', text, re.I):
        return ''
    
    return text

def _cut_text_if_needed(text):
    
    
    # text might be too long because this is the last
    # legal footnote. so cut it along markers that would
    # not be OK to cut on normally.
    
    for regex in LFRC.get_cutting_regexes():
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
            
            if i & 1 == 1:
                recorder.append(hits[i])
                continue
            
            if not record_text:
                if _check_whether_header_is_valuable(i, hits) and _check_whether_chunk_is_new_section(i, hits):
                    record_text = True
                    record_header, recorder = _set_up_recorder(i, hits)
            
            elif _check_if_valid_ending(i, hits):
                    record_text = False
                    record = ''.join(blob for blob in recorder)
                        
                    record = _cut_text_if_needed(record)
                    
                    if re.search("SUBSEQUENT", record_header, re.I):
                        record = _subsequent_event_text_handler(record)
                    
                    if record_header not in results:
                        results[record_header] = list()
                        
                    results[record_header].append(record + '\n\n')
                    
                    recorder = list()
                    record_header = None
                    
                    if _check_whether_header_is_valuable(i, hits) and _check_whether_chunk_is_new_section(i, hits):
                        record_text = True
                        record_header, recorder = _set_up_recorder(i, hits)    
            else:
                recorder.append(hits[i])
        
        if len(recorder) > 0 and record_header is not None:
            
            record = ''.join(blob for blob in recorder)
                        
            record = _cut_text_if_needed(record)
            
            if re.search("SUBSEQUENT", record_header, re.I):
                record = _subsequent_event_text_handler(record)
            
            if record_header not in results:
                results[record_header] = list()

            results[record_header].append(record + '\n\n')
                
        if _are_results_from_this_regex_split_acceptable(results):
            # one type of regex is used. only one. notes don't take on different formats within the 10-K.
            break           

    return ''.join(''.join(blob for blob in results[key]) + '\n\n' for key in results)

def _are_results_from_this_regex_split_acceptable(results):
    
    return len(results) > 0

def _edit_text_to_remove_periods(text):
    ''' rip out common places for periods for easier parsing '''

    # periods right after common demarcations
    text = re.sub("(?P<section>(Note|Item)\s*[0-9]+)\s*\.", "\g<section> ", text, flags = re.I | re.M | re.S)
    
    # decimal points
    for _ in xrange(5):
        text = re.sub("(?P<before>[0-9]+)\.(?P<after>[0-9]+)", "\g<before>\g<after>", text, flags=re.I | re.M | re.S)
    
    # names with middle initials
    text = re.sub("(?P<before>[A-Z][a-z]+) +[A-Z]\.\s+(?P<after>[A-Z][a-z]+)", "\g<before>\g<after>", text, flags=re.M | re.S)
    
    # common abbreviations with periods.
    text = re.sub("U\s*\.\s*S\.\s*C\.", "USC", text, flags=re.I | re.M | re.S)
    text = re.sub("B\.\s*S\.\s*C\.", " BSC ", text, flags=re.I | re.M | re.S)

    text = re.sub("U\s*\.\s*S\.", "US", text, flags=re.I | re.M | re.S)
    text = re.sub("D\s*\.\s*C\.", "DC", text, flags=re.I | re.M | re.S)
    text = re.sub("N\s*\.\s*A\.", "NA", text, flags=re.I | re.M | re.S)
    text = re.sub("K\s*\.\s*K\.", "KK", text, flags=re.I | re.M | re.S)
    text = re.sub("No\.", "No", text, flags=re.M | re.S) 
    
    text = re.sub("(?P<before>[A-Z])\s*\.(?P<after>[A-Z])\s*\.", "\g<before>\g<after>", text, flags=re.I | re.M | re.S)
    
    return text

def _remove_common_irrelevant_number_patterns(text):
    
    # years.
    text = re.sub("20[0-7][0-9]", "year", text)
    text = re.sub("19[8-9][0-9]", "year", text)

    return text
    
def get_best_litigation_note_hits(text):
    
    text = _edit_text_to_remove_periods(text)
    text = _remove_common_irrelevant_number_patterns(text)
    
    return _get_all_viable_hits(text)
    