'''
Created on Jul 11, 2012

@author: mchrzanowski
'''

import litigationfootnoteparsing as lfp
import nltk
import re
import Utilities


def get_programming_fragment_check():
    return re.compile("XML|/td|\sdiv\s|\svalign\s|falsefalse|truefalse|falsetrue" + \
                 "|link:[0-9]+px|font-family|link:|background-color|utf-8;" + \
                 "|us-gaap:|px|\sfont\s", re.I)

def _check_whether_previous_section_ended_with_a_month(location, hits):
    
    punctuated_tokens = lfp.wordtokencreation.punctuate_prior_section(location, hits)
    if re.match("(Jan((uary)|[^A-Za-z])|Feb((ruary)|[^A-Za-z])|mar((ch)|[^A-Za-z])|apr((il)|[^A-Za-z])|may)", punctuated_tokens[-1], re.I):
        return True
    
    if re.match("(jun((e)|[^A-Za-z])|july|aug((ust)|[^A-Za-z])|sept((ember)|[^A-Za-z])|oct((ober)|[^A-Za-z]))", punctuated_tokens[-1], re.I):
        return True
    
    if re.match("(nov((ember)|[^A-Za-z])|dec((ember)|[^A-Za-z]))", punctuated_tokens[-1], re.I):
        return True
    
    return False

def does_previous_section_end_with_a_common_word_that_preceeds_a_number(location, hits):
    ''' check to make sure the last few words don't contain common words 
    that have numbers after them.'''
    
    punctuated_tokens = lfp.wordtokencreation.punctuate_prior_section(location, hits)
    if re.match("ITEM|NOTE(?!S)|Section|region|division|unit|units", punctuated_tokens[-1], re.I):
        return True

    if _check_whether_previous_section_ended_with_a_month(location, hits):
        return True
    
    last_sentence_fragment = lfp.wordtokencreation.get_last_sentence_fragment(location, hits, return_as_string=True) 
    if re.search("Units?\s*[0-9]*$", last_sentence_fragment) \
    or re.search("Region\s*[0-9]*$", last_sentence_fragment) \
    or re.search("USC\s*[0-9]*$", last_sentence_fragment):
    #    #print "MATCH on end words with numbers attached."
        return True
    
    return False
    
def are_there_more_left_parentheses_than_right_parentheses(location, hits):
    
    last_sentence_fragment = lfp.wordtokencreation.get_last_sentence_fragment(location, hits, return_as_string=True) 
    char_frequency = Utilities.character_counter(last_sentence_fragment, '(', ')')
        
    if char_frequency['('] > char_frequency[')']:
        return True
    
    return False

def does_previous_section_end_with_a_complete_parenthetical_block(location, hits):
    compressed_fragment = lfp.wordtokencreation.get_last_sentence_fragment(location, hits, return_as_string=True) 
    
    if re.search("^\(.*\)$", compressed_fragment, flags=re.M | re.S):
        #print 'MATCH on parens end'
        return True
    
    return False
    
    
def check_whether_previous_section_ended_with_note_when_the_tokenization_uses_note(location, hits):
    ''' did the last section end with note *something*, and did the current section start with
    note? if so, we can move on; this is a new sentence. '''
    punctuated_tokens = lfp.wordtokencreation.punctuate_prior_section(location, hits)
    if re.match("Note(?!S)", punctuated_tokens[-2], re.I) and re.search("Note(?!S)", hits[location - 1], re.I):
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

def check_cases_of_previous_section_token_and_current_token(location, hits, current_header_location):
    ''' make sure this section's Notes header case matches the current header's case. '''
    
    if current_header_location is not None and re.search("Note(?!S)", hits[current_header_location], re.I) \
    and re.search("Note(?!S)",  hits[location - 1], re.I) \
    and not _check_equality_of_two_note_tokens(hits[current_header_location], hits[location - 1]):
        return True
    
    return False
    
def check_whether_token_numbers_are_near_each_other(location, hits, current_header_location):
    ''' if the current header's token has a number in it, then we expect the ending token
    to be sort of close to that number. so, if the number is greater than the current header token,
    we're still in the same section. don't check whether the number is smaller than the current header token
    as in the case of the last footnote, the ending that got picked up might be some agreement in the 
    last sections of the 10-K, and those typically start from 1 again. '''
    
    if current_header_location is not None and re.search("[0-9]+", hits[current_header_location]) \
    and re.search("[0-9]+", hits[location - 1]):
        current_header_number = re.search("(?P<number>[0-9]+)", hits[current_header_location])
        potential_header_number = re.search("(?P<number>[0-9]+)", hits[location - 1])
        
        if int(potential_header_number.group('number')) > 4 + int(current_header_number.group('number')):
            #print "match on number"
            return True
        
    return False

def did_last_section_end_with_punct_mark(location, hits):
    ''' check to see whether the previous section ended with a punct mark '''
    punctuated_tokens = lfp.wordtokencreation.punctuate_prior_section(location, hits)
    return re.match("[.?!]", punctuated_tokens[-1][-1])

def does_last_sentence_of_preceeding_section_end_on_a_commonly_incorrect_cut_pattern(location, hits):
    
    last_sentence_fragment = lfp.wordtokencreation.get_last_sentence_fragment(location, hits)
    
    if last_sentence_fragment is None:
        return False
    
    for word in last_sentence_fragment:

        # found special word. this is not a complete sentence.
        # these special words are here because there are all sorts of garbage sections
        # that have verbs but are actually the text from graphs and charts.
        if re.search("see|under|SUMMARIZEd|included|DISCUSS|REFER|describe|disclose|violate|approve|further", word, re.I): 
            #print "MATCH:", word
            return True
    
    return False

def was_cut_within_a_table(location, hits):
    
    if does_last_sentence_of_preceeding_section_end_on_a_commonly_incorrect_cut_pattern(location, hits):
        
        last_sentence_fragment = lfp.wordtokencreation.get_last_sentence_fragment(location, hits)
        
        compressed_sentence_fragment = lfp.wordtokencreation.get_last_sentence_fragment(location, hits, return_as_string=True)

        # now, do additional checks to see whether we picked up a table. 
        # tables normally have units of currency as well as the word follows somewhere.
        # if these hold, then we're probably in a table from a previous section.
        # that means that if we're in a relevant section right now, and the new hit demarcates a new section,
        # then we want to stop recording. if we're not recording, then we probably want to start.
        # if we're in a relevant section and the new hit does *not* have a header that's been whitelisted as being
        # a section, then we can continue recording.
        if re.search("(in)?\s*(millions|thousands|billions)", compressed_sentence_fragment, re.I | re.M | re.S) \
        and re.search("total|follows", compressed_sentence_fragment, re.I | re.M | re.S):
            #print "MATCH ON currency"
            #print 'MATCH ON FOLLOWS|total'
            return True
            
        char_frequency = Utilities.character_counter(compressed_sentence_fragment, '$')
        
        if char_frequency['$'] >= 6:
            #print 'MATCH ON DOLLAR COUNT'
            return True
        
        number_count = 0
        for word in last_sentence_fragment:
            if Utilities.contains_numbers(word):
                number_count += 1
                
        if re.search("total|follows|balance", compressed_sentence_fragment, re.I | re.M | re.S) \
        and number_count >= 6:
            #print "match on number count"
            return True
    
    return False
