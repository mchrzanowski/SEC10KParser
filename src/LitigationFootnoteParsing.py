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
        
def _check_if_valid_ending(location, hits, current_header_location):
    
    # the token is white space. end it when whitelisted headers are encountered.
    if not re.search("[0-9A-Za-z]", hits[current_header_location]):
        if _check_whether_current_section_header_is_whitelisted_as_new_section(location, hits):
            return True
        else:
            return False
    
    elif _check_whether_section_is_part_of_another_section(location, hits, current_header_location) \
    or _check_whether_header_is_valuable(location, hits):
        return False
    
    else:
        return True
    
def _check_whether_current_section_header_is_whitelisted_as_new_section(location, hits):
    
    compressed_header = ''.join(_get_header_of_chunk(location, hits))
    
    for legitimate_header in LFRC.get_legitimate_headers():
        if re.search(legitimate_header, compressed_header):
            return True
        
    return False
    
def _check_equality_of_two_note_tokens(first_token, second_token):
    
    if first_token is None or second_token is None:
        return False
    
    first = re.search("(?P<note>Note)", first_token, re.I)
    second = re.search("(?P<note>Note)", second_token, re.I)
    
    if first and second:
        return first.group('note') == second.group('note')
    
    return False

_another_section_cache = dict()
def _check_whether_section_is_part_of_another_section(location, hits, current_header_location):
    
    #print "CHECKING TO SEE WHETHER PART OF ANOTHER SECTION", hits[location]
    
    # if we are recording a section of the 10-K, and we have stumbled upon a section
    # that does not have lettering, then continue onwards.
    if current_header_location is not None and not re.search("[A-Za-z]", hits[location]):
        return True
    
    if hits[location] in _another_section_cache:
        punctuated_tokens = _another_section_cache[hits[location]]
    else:
        text_before_slice = ''.join(hit for num, hit in enumerate(hits) if num <= location - 2 and location >= 5 * num // 6)
        # strip everything except those words after the last punctuation mark.
        punctuated_tokens = nltk.punkt.PunktWordTokenizer().tokenize(text_before_slice)
        _another_section_cache[hits[location]] = punctuated_tokens
    
    # check to make sure the last few words don't contain common words 
    # that have numbers after them.
    if re.match("ITEM|NOTE(?!S)|Section|region|division|unit|units", punctuated_tokens[-1], re.I):
        #print 'MATCH ON end word regex'
        return True
    
    # did the last section end with note *something*, and did the current section start with
    # note? if so, we can move on; this is a new sentence.
    if re.match("Note(?!S)", punctuated_tokens[-2], re.I) and re.search("Note(?!S)", hits[location - 1], re.I):
        return False
    
    # make sure this section's Notes header case matches the current header's case.
    if current_header_location is not None and re.search("Note(?!S)", hits[current_header_location], re.I) \
    and re.search("Note(?!S)",  hits[location - 1], re.I) \
    and not _check_equality_of_two_note_tokens(hits[current_header_location], hits[location - 1]):
        return True
    
    # if the current header's token has a number in it, then we expect the ending token
    # to be sort of close to that number. so, if the number is greater than the current header token,
    # we're still in the same section. don't check whether the number is smaller than the current header token
    # as in the case of the last footnote, the ending that got picked up might be some agreement in the 
    # last sections of the 10-K, and those typically start from 1 again.
    if current_header_location is not None and re.search("[0-9]+", hits[current_header_location]) \
    and re.search("[0-9]+", hits[location - 1]):
        current_header_number = re.search("(?P<number>[0-9]+)", hits[current_header_location])
        potential_header_number = re.search("(?P<number>[0-9]+)", hits[location - 1])
        
        if int(potential_header_number.group('number')) > 4 + int(current_header_number.group('number')):
            #print "match on number"
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
            #    #print "MATCH on end words with numbers attached."
                return True
            
            char_frequency = Utilities.character_counter(compressed_fragment, '(', ')', '$')
            
            if char_frequency['('] > char_frequency[')']:
                return True
            
            found_special_word_that_might_be_from_a_table = False                
            
            for word in punctuated_tokens[end_of_last_sentence_index + 1:]:     # check the last sentence fragment. 

                # found special word. this is not a complete sentence.
                # these special words are here because there are all sorts of garbage sections
                # that have verbs but are actually the text from graphs and charts.
                if re.search("see|under|SUMMARIZEd|included|DISCUSS|REFER|describe|disclose|violate|approve|further", word, re.I): 
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
                
                if char_frequency['$'] >= 6:
                    #print 'MATCH ON DOLLAR COUNT'
                    return False
                
                number_count = 0
                for word in punctuated_tokens[end_of_last_sentence_index + 1:]:
                    if Utilities.contains_numbers(word):
                        number_count += 1
                        
                if re.search("total|follows|balance", compressed_fragment, re.I | re.M | re.S) \
                and number_count >= 6:
                    #print "match on number count"
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
    
def _check_whether_chunk_is_new_section(location, hits, current_token_location):
    
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
   
    if _check_whether_section_is_part_of_another_section(location, hits, current_token_location):
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
        return False
    
    #print "Amendment check pass"
    
    # ditto for "this Agreement"
    if re.search("this\s*Agreement", hits[location][:500]):
        return False
    
    #print "Agreement check pass"

    return True

def _get_header_of_chunk(location, hits):
    ''' return the header '''
    if hits[location] in _word_tokenize_cache:
        words = _word_tokenize_cache[hits[location]]
    else:
        words = nltk.word_tokenize(hits[location])
        _word_tokenize_cache[hits[location]] = words
        
    return_list = list()
    for piece in words:
        if re.search("[A-Z0-9a-z]", piece):
            return_list.append(piece)
        
        if len(return_list) == 4:
            break
    
    return return_list
    

def _check_whether_header_is_valuable(location, hits):
    
    header = _get_header_of_chunk(location, hits)
    
    #print "CHECKING HEADER:", header
    
    # header *has* to contain some special keywords.
    contains_keyword = False    
    for word in header:
        if re.match("D[eE][bB][tT]|" + \
        "L[iI][tT][iI][gG][aA][tT][iI][oO][nN]|" + \
        "C[oO][nN][tT][iI][nN][gG][eE][nN][tTcC]|" + \
        "C[oO][mM][mM][iI][tT][mM][eE][nN][tT]|" + \
        "P[rR][oO][cC][eE][eE][dD][iI][nN][gG]|" + \
        "C[oO][nN][tT][iI][gG][eE][nN][cC][iI][eE][sS]|" + \
        "L[eE][gG][aA][lL]|" +
        "S[uU][bB][sS][eE][qQ][uU][eE][nN][tT]|" + \
        "O[tT][hH][eE][rR]", word):
            contains_keyword = True
            #print word, header
            break
        
    if not contains_keyword:
        return False

    # now check for common bigrams that we don't want.
    compressed_header = ''.join(word for word in header)
    
    #print header
    #print compressed_header
    
    # debt or other by themselves are not useful.
    if re.search("D[eE][bB][tT]|O[tT][hH][eE][rR]", compressed_header) \
    and not re.search("Litigation|Contingenc|Commitment|Proceeding|" + \
                      "Contigencies|Legal|Subsequent", compressed_header, re.I):
        return False
    
    for regex in LFRC.get_names_of_headers_we_dont_want():
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
    
    # three-digit numbers are also never present.
    for blob in header:
        if re.match("[0-9]{3}", blob):
            #print "MATCH ON TRIPLE NUMBER"
            return False
    
    return True

def _does_section_mention_litigation(text):
    return re.search('litigation|legal|jury|verdict', text, re.I)

def _cut_text_if_needed(text):
    
    # text might be too long because this is the last
    # legal footnote. so cut it along markers that would
    # not be OK to cut on normally.
    
    for regex in LFRC.get_cutting_regexes():
        if re.search(regex, text):
            text = re.sub(regex, "", text)
        
    return text

def _set_up_recorder(location, hits):
    recorder = list()
    record_header = ''.join(_get_header_of_chunk(location, hits))
    #print "CREATED:", record_header
    recorder.append(hits[location - 1])   # assuming this is the token.
    recorder.append(hits[location])
    return record_header, recorder, location - 1

def _transform_list_of_hits_into_result(recorder, record_header):
    record = ''.join(recorder)
    record = _cut_text_if_needed(record)
    
    if re.search("SUBSEQUENT", record_header, re.I):
        if not _does_section_mention_litigation(record):
            record = None
    
    return record

def _get_all_viable_hits(text):
    
    results = dict()
    
    for regex in LFRC.get_document_parsing_regexes():
        
        #print "NEW regex:", regex.pattern
        
        hits = re.split(regex, text)
        
        record_text = False
        record_header = None
        current_token_location = None
        recorder = list()
        
        for i in xrange(len(hits)):
            
            # odd-numbered indices have tokens inside them.
            if i & 1 == 1:
                recorder.append(hits[i])
                continue
            
            if not record_text:
                if _check_whether_header_is_valuable(i, hits) and _check_whether_chunk_is_new_section(i, hits, current_token_location):
                    record_text = True
                    record_header, recorder, current_token_location = _set_up_recorder(i, hits)
            
            elif _check_if_valid_ending(i, hits, current_token_location):
                    
                    record = _transform_list_of_hits_into_result(recorder, record_header)
                    
                    if record is not None:
                        if record_header not in results:
                            results[record_header] = list()
                        results[record_header].append(record + '\n\n')

                    record_text = False
                    record_header = None
                    current_token_location = None
                    recorder = list()
                    
                    if _check_whether_header_is_valuable(i, hits) and _check_whether_chunk_is_new_section(i, hits):
                        record_text = True
                        record_header, recorder, current_token_location = _set_up_recorder(i, hits)    
            else:
                recorder.append(hits[i])
        
        if len(recorder) > 0 and record_header is not None:
            
            record = _transform_list_of_hits_into_result(recorder, record_header)
            
            if record is not None:
                if record_header not in results:
                    results[record_header] = list()
                results[record_header].append(record + '\n\n')
                
        if _are_results_from_this_regex_split_acceptable(results):
            # one type of regex is used. only one. notes don't take on different formats within the 10-K.
            break           

    return ''.join(''.join(results[key]) + '\n\n' for key in results)

def _are_results_from_this_regex_split_acceptable(results):
    return len(results) > 0

def _edit_text_to_remove_periods(text):
    ''' rip out common places for periods for easier parsing '''

    # periods right after common demarcations
    text = re.sub("(?P<section>(Note|Item)\s*[0-9]+)\s*\.", "\g<section> ", text, flags = re.I | re.M | re.S)
    
    # deal with decimal numbers. do this one several time as sometimes, the whitespace is so bad
    # that the numbers run into each other. each pass removes a few of the decimal points.
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
    