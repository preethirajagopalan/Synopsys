#!/opt/python-2.7.13/bin/python -u

import re

def parse_info(search_term, output, num_groups, find_string=None):
    """
    :type search_term: string
    :type output: string
    :type num_groups: int
    :type find_string: string
    :rtype: List[string]

    Looks through output using the given regex search string. num_groups is the number of expected capture groups. This is used in favor of re.findall
    in certain situations, as re.findall returns a list of tuples, which requires extra work to parse. Returns an empty list if no match can be found,
    else returns a list of the parsed capture groups.

    EXAMPLE USAGE:
    info = parse_info(r'(\S+) (\S+ \S+)', 'this is a test', 2, find_string=' is')
    """
    # finds the string index first to truncate output
    if (find_string):
        index = output.find(find_string)
        if (index == -1): 
            return []
        output = output[index:]

    match = re.search(search_term, output)

    # indicates that the phrase could not be found
    if (not match): 
        return []

    # gets each individual terms
    return [match.group(num) for num in range(1, num_groups + 1)]