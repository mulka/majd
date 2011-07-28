#!/usr/bin/env python
import os
import re
import json

def jwi_helper(f, input):
    if isinstance(input, dict):
        output = {}
        for k in input:
            output[k] = jwi_helper(f, input[k])
    elif isinstance(input, list):
        output = []
        for i in range(len(input)):
            output.append(jwi_helper(f, input[i]))
    else:
        m = re.match("@include:(.*)", str(input))
        if m:
            output = load_json_with_includes('tests/partials/' + m.group(1) + '.json')
        else:
            output = input
    return output

def load_json_with_includes(filename):
    f = open(filename)
    input = json.loads(f.read())
    return jwi_helper(filename, input)
    
def var_replace_helper(vars, variable, value):
    if isinstance(variable, dict):
        output = {}
        for k in variable:
            output[k] = var_replace_helper(vars, variable[k], value[k])
    elif isinstance(variable, list):
        output = []
        for i in range(len(variable)):
            output.append(var_replace_helper(vars, variable[i], value[i]))
    else:
        if ((isinstance(variable, unicode) or isinstance(variable, str)) and variable[0] == '$'):
            vars[variable] = value
            output = value
        else:
            output = variable

    return output

def var_replace(with_variables, with_values):
    """
    >>> var_replace("$session_id", "aoeuidhtns")
    ({'$session_id': 'aoeuidhtns'}, 'aoeuidhtns')

    >>> var_replace({'session_id': '$session_id'}, {'session_id': 'aoeuidhtns'})
    ({'$session_id': 'aoeuidhtns'}, {'session_id': 'aoeuidhtns'})

    >>> var_replace(['$count1','$count2', '$count3'], [4, 5, 6])
    ({'$count1': 4, '$count2': 5, '$count3': 6}, [4, 5, 6])

    >>> var_replace({'counts': ['$count1','$count2', '$count3']}, {'counts': [4, 5, 6]})
    ({'$count1': 4, '$count2': 5, '$count3': 6}, {'counts': [4, 5, 6]})

    """
    vars = {}
    output = var_replace_helper(vars, with_variables, with_values)
    return vars, output

if __name__ == "__main__":
    import doctest
    doctest.testmod()