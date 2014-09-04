'''
Created on Aug 6, 2014

@author: kyleg
'''

import re
"""
This module encodes a string using Soundex, as described by
http://en.wikipedia.org/w/index.php?title=Soundex&oldid=466065377

Only strings with the letters A-Z and of length >= 2 are supported.
"""

invalid_re = re.compile("[AEHIOUWY]|[^A-Z]")
numerical_re = re.compile("[A-Z]")

charsubs = {'B': '1', 'F': '1', 'P': '1', 'V': '1',
            'C': '2', 'G': '2', 'J': '2', 'K': '2',
            'Q': '2', 'S': '2', 'X': '2', 'Z': '2',
            'D': '3', 'T': '3', 'L': '4', 'M': '5',
            'N': '5', 'R': '6'}

#numlist = ['1','2','3','4','5','6','7','8','9','0']

def normalize(s):
    """ Returns a copy of s without invalid chars and repeated letters. """
    # remove invalid chars
    first = s[0].upper()
    s = re.sub(invalid_re, "", s.upper()[1:])
    # remove repeated chars
    char = None
    
    s_clean = first

    for c in s:
        if char != c:
            s_clean += c
        char = c

    return s_clean


def soundex(s):
#""" Encode a string using Soundex.
#Takes a string and returns its Soundex representation.
#"""
    if len(s) < 2:
        return None
    s = normalize(s)
    last = None
    enc = s[0]
    for c in s[1:]:
        if len(enc) == 4:
            break
        if charsubs[c] != last:
            enc += charsubs[c]
        last = charsubs[c]
    while len(enc) < 4:
        enc += '0'
    return enc

def numdex(s):
    if s[0] in ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0']:
        numerical_re = re.compile("[A-Z]|[^0-9][^0-9][^0-9][^0-9]")
        s=re.sub(numerical_re,"", s.zfill(4))
        return s.zfill(4)
    else:
        return soundex(s)


    
    
if __name__ == "__main__":
    import doctest
    doctest.testmod()