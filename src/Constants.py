'''
Created on Jun 8, 2012

@author: mchrzanowski
'''

import os.path
import re

CIK_CODE_LENGTH = 10

FLAG_INDICATING_VERB_SHOULD_BE_SKIPPED = '#'

PATH_TO_CORPUS = './corpus/'

COMPANY_NAME_AND_CIK_MAPPING_FILE_DELIMITER = "==========================="

PATH_TO_COMPANY_NAME_AND_CIK_MAPPING_FILE = os.path.join(PATH_TO_CORPUS, 'company_CIK_to_name_mapping.txt')

PATH_TO_LEGAL_FOOTNOTE_CORPUS = os.path.join(PATH_TO_CORPUS, 'legal_footnotes')

PATH_TO_LEGAL_PROCEEDING_CORPUS = os.path.join(PATH_TO_CORPUS, 'legal_proceedings')

PATH_TO_FAILED_UNIT_TESTS = './failed_tests/'

PATH_TO_DROPBOX_DIRECTORY = "/home/polak/Dropbox/Corporate Litigation Research/Edgar Corpus/"

PATH_TO_RAW_URL_DATA = '/home/polak/raw_data_corpus/'

PATH_TO_PROCESSED_URL_DATA = '/home/polak/processed_data_corpus/'

PATH_TO_VERB_FILE = os.path.join(os.curdir, '../etc/common_verbs.txt')

SEC_WEBSITE = "http://www.sec.gov/"

REGRESSION_CHAR_COUNT_CHANGE_THRESHOLD = 0.1
