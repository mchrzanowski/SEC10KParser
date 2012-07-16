'''
Created on Jun 13, 2012

@author: mchrzanowski
'''

import litigationfootnoteparsing as lfp
import nltk
import re
import Utilities
import verbclassifier

def _check_if_valid_ending(location, hits, current_header_location):
    
    # the token is white space. end it when whitelisted headers are encountered.
    if not re.search("[0-9A-Za-z]", hits[current_header_location]):
        if _check_whether_current_section_header_is_whitelisted_as_new_section(location, hits):
            return True
        else:
            return False
    
    elif _check_whether_section_is_part_of_another_section(location, hits, current_header_location) \
    or lfp.headervalidity.check_whether_header_is_valuable(location, hits):
        return False
    
    else:
        return True
    
def _check_whether_current_section_header_is_whitelisted_as_new_section(location, hits):
    
    compressed_header = ''.join(lfp.headervalidity.get_header_of_chunk(location, hits))

    for legitimate_header in lfp.headerpatternrepository.get_legitimate_headers():
        if re.search(legitimate_header, compressed_header):
            return True
        
    return False

def _check_whether_section_is_part_of_another_section(location, hits, current_header_location):
    
    #print "CHECKING TO SEE WHETHER PART OF ANOTHER SECTION:", hits[location]

    #print "Fragment:", lfp.wordtokencreation.get_last_sentence_fragment(location, hits, return_as_string=True)
    
    # if we are recording a section of the 10-K, and we have stumbled upon a section
    # that does not have lettering, then continue onwards.
    if current_header_location is not None and not re.search("[A-Za-z]", hits[location]):
        #print "match on no alphanumeric match"
        return True
    
    # check to make sure the last few words don't contain common words 
    # that have numbers after them.
    if lfp.tokenvalidity.does_previous_section_end_with_a_common_word_that_preceeds_a_number(location, hits):
        #print "match on common word ending"
        return True

    if re.match("^[\s0-9]+[\s.?!:]?$", hits[location - 1]) and \
    lfp.tokenvalidity.does_previous_section_end_with_a_word_with_an_uncommon_capitalized_word(location, hits):
        return True
    
    # did the last section end with note *something*, and did the current section start with
    # note? if so, we can move on; this is a new sentence.
    if lfp.tokenvalidity.check_whether_previous_section_ended_with_note_when_the_tokenization_uses_note(location, hits):
        #print 'match on note ending'
        return False
    
    if lfp.tokenvalidity.check_cases_of_previous_section_token_and_current_token(location, hits, current_header_location):
        #print 'MATCH ON note casing'
        return True
    
    if lfp.tokenvalidity.check_whether_token_numbers_are_near_each_other(location, hits, current_header_location):
        #print "MATCH ON numerical proximity"
        return True
    
    # everything is contained in parentheses? probably OK.
    if lfp.tokenvalidity.does_previous_section_end_with_a_complete_parenthetical_block(location, hits):
        #print "parenthetical block ending"
        return False
    
    if lfp.tokenvalidity.are_there_more_left_parentheses_than_right_parentheses(location, hits):
        #print "match on left versus right parenths"
        return True
   
    # a true value means that yes, we were in a table. 
    # now, ask: are we recording a segment right now? if so, continue recording
    # UNLESS this next section is itself its own section.
    if lfp.tokenvalidity.was_cut_within_a_table(location, hits):
        #print "inside table"
        if current_header_location is None \
        or _check_whether_current_section_header_is_whitelisted_as_new_section(location, hits):
            #print "start over"
            return False
        else:
            #print "continue recording"
            return True
    
    # did the last section include something like "SEE"? those words typically indicate
    # that not we're in a standalone section. 
    # make sure the last word doesnt end with "NOTE" as we pre-process periods out containing that word.
    if lfp.tokenvalidity.does_last_sentence_of_preceeding_section_end_on_a_commonly_incorrect_cut_pattern(location, hits) \
    and not lfp.tokenvalidity.does_last_section_end_with_note(location, hits):
        #print "matchon on common cut pattern"
        return True
   
    return False

def _does_section_contain_verbs(words):
    
    contains_verbs = False
    for word in words:
        if verbclassifier.is_word_a_common_verb(word):
            #print "VERB MATCH:", word
            contains_verbs = True
            break
    
    return contains_verbs
    
def _check_whether_chunk_is_new_section(location, hits, current_token_location):
    
    #print "CHECKING:", hits[location]

    words_in_hit = lfp.wordtokencreation.word_tokenize_hit(location, hits)
    
    # does it contain verbs? detritus usually doesn't.    
    if not _does_section_contain_verbs(words_in_hit):
        #print "match on verb check"
        return False
    
   
    if _check_whether_section_is_part_of_another_section(location, hits, current_token_location):
        #print "match on fragment check"
        return False
        
    # does it contain weird XML/HTML elements in the top-most section? 
    # probably not what we want.
    
    top_section = ''.join(blob for blob in re.split("\n\n+", hits[location])[:3])
        
    if re.search(lfp.hitprocessing.get_programming_fragment_check(), top_section):
        #print "match on JUNK TAG CHECK"
        return False
    
    
    # does it contain the phrase "this Amendment"? If so, it's probably not what we want.
    if re.search("this\s*Amendment", top_section):
        #print "match on Amendment check"
        return False
    
    
    # ditto for "this Agreement"
    if re.search("this\s*Agreement", hits[location][:500]):
        #print "match on  Agreement check"
        return False

    if re.search("RESTATED\s*CREDIT\s*AGREEMENT", hits[location][:1000], re.I | re.M):
        #print "match on rca"
        return False
    
    if re.search("Basis\s*of\s*Presentation", hits[location][:500], re.M):
        #print "match on bop"
        return False

    # does the first chunk contain the phrase 
    # "of the Notes to Consolidated Financial Statements"?
    # this normally means this section was part of a previous section.
    if re.search("(of|in)\s*the\s*Notes\s*to\s*(the)?\s*Consolidated", hits[location][:500], re.I | re.M) \
    and not re.search("except\s*as\s*follows", hits[location][:500], re.I | re.M):
        #print "match on of the"
        return False

    if re.search("Administrative\s*Agent", hits[location][:500], re.M):
        #print "match on admin agent"
        return False
    
    if re.search("(Borrower|Guarantor|Licensee|Lender|Holder|Execution\s*Date)[^a-zA-Z]", hits[location][:500]):
        #print "match on bgllhed"
        return False

    if re.search("Consulting\s*Period|Closing|Transferred\s*Subsidiary|Exhibit[^s]", hits[location][:500]):
        #print "match on cpctse"
        return False

    if re.search("Item\s*3[\s\.]*Legal\s*Proceeding", hits[location][:500], re.I):
        #print "match on item 3"
        return False

    if re.search("(Share|Stock)holders.*Equity", hits[location][:500], re.I):
        #print "match on ste"
        return False

    return True

def _does_section_mention_litigation(text):
    return re.search('litigation|legal|jury|verdict', text, re.I)

def _cut_text_if_needed(text):
    
    # text might be too long because this is the last
    # legal footnote. so cut it along markers that would
    # not be OK to cut on normally.
    
    for regex in lfp.hitprocessing.get_cutting_regexes():
        if re.search(regex, text):
            text = re.sub(regex, "", text)
        
    return text

def _set_up_recorder(location, hits):
    recorder = list()
    record_header = ''.join(lfp.headervalidity.get_header_of_chunk(location, hits))
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

    # almost all records are at least X chars. if not, it's 
    # probably something that we don't want.
    if record is not None and Utilities.get_alpha_numeric_count(record) < 200:
        record = None
    
    return record

def _get_all_viable_hits(text):
    
    results = dict()
    
    for regex in lfp.documenttokens.get_document_parsing_regexes():
        
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
                if lfp.headervalidity.check_whether_header_is_valuable(i, hits) \
                and _check_whether_chunk_is_new_section(i, hits, current_token_location):
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
                    
                    if lfp.headervalidity.check_whether_header_is_valuable(i, hits) \
                    and _check_whether_chunk_is_new_section(i, hits, current_token_location):
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

def get_best_litigation_note_hits(text):
    text = lfp.preprocessing.sanitize_text(text)
    return _get_all_viable_hits(text)
    