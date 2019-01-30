'''
Module to load comment-containing JSON. For this module, comments must be on a
line by themselves and must start with two slashes (//).
'''

import json
import re

def loads(string):
    multiline_comments = re.compile(r'/\*'
                                    r'.*?' # Non-greedy matching
                                    r'\*/', re.DOTALL)
    line_endings = re.compile(r'[\r\n]+')
    string = multiline_comments.sub('', string)
    return json.loads('\n'.join(i for i in line_endings.split(string) if not i.strip().startswith('//')))

def load(filename):
    with open(filename) as f:
        return loads(f.readlines())

if __name__ == '__main__':
    exit('This is a library module not meant to be executed directly.')
