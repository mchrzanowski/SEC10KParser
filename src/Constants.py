'''
Created on Jun 8, 2012

@author: mchrzanowski
'''

import os.path

CIK_CODE_LENGTH = 10

FLAG_INDICATING_VERB_SHOULD_BE_SKIPPED = '#'

PATH_TO_CORPUS = './corpus/'

PATH_TO_LEGAL_FOOTNOTE_CORPUS = os.path.join(PATH_TO_CORPUS, 'legal_footnotes')

PATH_TO_LEGAL_PROCEEDING_CORPUS = os.path.join(PATH_TO_CORPUS, 'legal_proceedings')

PATH_TO_FAILED_UNIT_TESTS = './failed_tests/'

PATH_TO_PROCESSED_URL_DATA = './processed_url_data/'

SEC_WEBSITE = "http://www.sec.gov/"

REGRESSION_CHAR_COUNT_CHANGE_THRESHOLD = 0.1
