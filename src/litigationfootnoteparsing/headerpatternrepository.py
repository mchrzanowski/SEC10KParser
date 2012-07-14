'''
Created on Jul 11, 2012

@author: mchrzanowski
'''

import re

def get_pattern_of_headers_we_want():
    return re.compile("D[eE][bB][tT]|" + \
        "L[iI][tT][iI][gG][aA][tT][iI][oO][nN]|" + \
        "C[oO][nN][tT][iI][nN][gG][eE][nN][tTcC]|" + \
        "C[oO][mM][mM][iI][tT][mM][eE][nN][tT]|" + \
        "P[rR][oO][cC][eE][eE][dD][iI][nN][gG]|" + \
        "C[oO][nN][tT][iI][gG][eE][nN][cC][iI][eE][sS]|" + \
        "L[eE][gG][aA][lL]|" +
        "S[uU][bB][sS][eE][qQ][uU][eE][nN][tT]|" + \
        "O[tT][hH][eE][rR]")

def get_patterns_of_headers_we_dont_want():
    ''' a list of patterns for headers we're not interested in '''
    return [re.compile("LEASE\s*COMMITMENT",  re.I | re.M),   \
        re.compile("ENERGY\s*COMMITMENT",  re.I | re.M),  \
        re.compile("Indemnity",  re.I),    \
        re.compile("Legal\s*Fees",  re.I | re.M), \
        re.compile("Reimbursement",  re.I), \
        re.compile("Assistance.*Litigation",  re.I | re.M | re.S), \
        re.compile("Contingent.*Interest",  re.I | re.M | re.S),  \
        re.compile("primarily", re.I), \
        re.compile("Performance\s*Contingenc", re.I | re.M) ]

def get_legitimate_headers():
    ''' a list of patterns of common headers '''
    return [re.compile("Performance\s*Objective", re.I | re.M), \
        re.compile("Commitment", re.I), \
        re.compile("The\s*Board\s*of\s*Directors\s*and\s*Stockholders", re.I | re.M), \
        re.compile("Forward.*looking\s*Statements", re.I | re.M | re.S), \
        re.compile("Shareholder.*EQUITY", re.I | re.M), \
        re.compile("Stockholder.*EQUITY", re.I | re.M), \
        re.compile("Contingencies", re.I), \
        re.compile("Long.*Term\s*Obligation", re.I | re.M), \
        re.compile("Notes?\s*Payable", re.I | re.M), \
        re.compile("Debt", re.I), \
        re.compile("Compensation", re.I), \
        re.compile("Legal", re.I), \
        re.compile("Litigation", re.I), \
        re.compile("Income\s*Taxes", re.I | re.M), \
        re.compile("Geographic\s*Information", re.I | re.M), \
        re.compile("Quarterly\s*Financial\s*Information", re.I | re.M), \
        re.compile("Subsequent", re.I), \
        re.compile("Significant\s*Accounting", re.I | re.M), \
        re.compile("Issued\s*Accounting\s*Pronouncements", re.I | re.M), \
        re.compile("Business\s*Segment", re.I | re.M), \
        re.compile("Discontinued\s*Operation", re.I | re.M), \
        re.compile("Diluted", re.I), \
        re.compile("Receivable", re.I), \
        re.compile("Inventor", re.I), \
        re.compile("Property\s*and\s*Equipment", re.I | re.M), \
        re.compile("Intangible\s*Assets", re.I | re.M), \
        re.compile("Goodwill", re.I), \
        re.compile("Accrued", re.I), \
        re.compile("Liabilit", re.I), \
        re.compile("Pension", re.I), \
        re.compile("Fair\s*Value", re.I | re.M), \
        re.compile("Guarant", re.I), \
        re.compile("Common\s*Share", re.I), \
        re.compile("Stock\s*Option", re.I), \
        re.compile("Parent\s*Company\s*Only", re.I), \
        re.compile("Related\s*Party\s*Transaction", re.I), \
        re.compile("Benefit\s*Plans", re.I), \
        re.compile("SEGMENTS?", re.I), \
        re.compile("Acquisitions?", re.I | re.M), \
        re.compile("Related\s*Part", re.I | re.M), \
        re.compile("Preferred\s*Securities", re.I | re.M), \
        re.compile("Stock.*Based", re.I | re.M), \
        re.compile("Restructuring", re.I), \
        re.compile("Environment", re.I ), \
        re.compile("Income\s*Tax", re.I), \
        re.compile("Ownership", re.I), \
        re.compile("Employee\s*Benefit", re.I), \
        re.compile("Share.*Based", re.I | re.M), \
        re.compile("Financial\s*Data", re.I), \
        re.compile("Liquidity", re.I), \
        re.compile("Restatement", re.I) ]
