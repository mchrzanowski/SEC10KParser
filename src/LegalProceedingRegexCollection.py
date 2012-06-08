'''
Created on Jun 7, 2012

@author: mchrzanowski
'''

def default():
    ''' so many 10-Ks have the litigation item structured thusly:
        Item 3. LITIGATION PROCEEDING
            blah blah
        Item 4. blah blah
        Item 5. blah blah
        
        take advantage of this by using the numbers as well as the fact that 
        the body is between these two Item headers 
    '''
        
    return "^\s*Item\s*?3.*?(?=Item\s*?4)"

def try_all_numbers_after_4():
    '''
         this regex is slightly different than the default regex: it allows
        for more matching on the Item number. Some 10-Ks miss Item 4 for some reason.
    '''
    return "^\s*Item\s*?3.*?(?=Item\s*?[5-9]+)"

