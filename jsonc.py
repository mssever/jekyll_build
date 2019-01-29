'''
Module to load comment-containing JSON. For this module, comments must be on a
line by themselves and must start with two slashes (//).
'''

import json
import re

def loads(string):
    if isinstance(string, str):
        string = re.split(r'[\r\n]+', string)
    elif not isinstance(string, list):
        raise TypeError('string must be a string or a list')
    return json.loads('\n'.join([i for i in string if not i.strip().startswith('//')]))

def load(filename):
    with open(filename) as f:
        return loads(f.readlines())

if __name__ == '__main__':
    exit('This is a library module not meant to be executed directly.')
