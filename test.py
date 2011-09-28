#!/usr/bin/env python
import urllib
import urllib2
try:
    import json
except:
    import simplejson as json
import uuid
import string
import time
from utils import var_replace, load_json_with_includes
from data_diff import data_diff

BASE_URL = 'http://localhost:8000/'

def call(base_url, method, session_id=None, data=None):
    url = base_url + method
    headers = {'Content-Type': 'application/json'}
    values = {}
    if data:
        values['data'] = data
    if session_id:
        values['session_id'] = session_id
    body = json.dumps(values)
    #print 'IN: ' + body
    req = urllib2.Request(url, body, headers)
    response = None
    try:
        response = urllib2.urlopen(req)
    except urllib2.HTTPError, e:
        response = e
    code = response.code
    res = response.read()
    #print 'OUT: ' + res
    return res

def fail(filename, step, method, input, expected, actual):
    print 'FAIL!'
    print 'FILE: ' + filename
    print 'STEP: ' + step
    print 'METHOD: ' + method
    print 'INPUT: ' + json.dumps(input)
    print 'EXPECTED: ' + json.dumps(expected)
    print 'ACTUAL: ' + json.dumps(actual)
    
def run_test(base_url, filename):
    
    #load test
    test = load_json_with_includes(filename)

    #set initial variables (might want to do this in the actual test config in the future)
    vars = {'$email': str(uuid.uuid4()) + '@example.com'}
    
    for i, step in enumerate(test):
        #replace variables in the input with values from vars
        try:
            input_json = json.dumps(step['input'])
            for k in vars:
                input_json = string.replace(input_json, k, vars[k])
            input = json.loads(input_json)
        except:
            input = {}
        
        try:
            session_id = input['session_id']
        except:
            session_id = None
            
        try:
            data = input['data']
        except:
            data = None
            
        actual_output_str = call(base_url, step['method'], session_id=session_id, data=data)
        try:
            actual_output = json.loads(actual_output_str)
        except Exception, e:
            fail(filename, str(i + 1), step['method'], input, step['output'], actual_output_str)
            raise e
        
        try:
            new_vars, replaced_output = var_replace(step['output'], actual_output)
        except Exception, e:
            fail(filename, str(i + 1), step['method'], input, step['output'], actual_output)
            raise e

        vars = dict(vars.items() + new_vars.items())
        try:
            diff = data_diff(replaced_output, actual_output)
            if diff:
                fail(filename, str(i + 1), step['method'], input, replaced_output, actual_output)
                exit()
        except Exception, e:
            fail(filename, str(i + 1), step['method'], input, replaced_output, actual_output)
            raise e

if __name__ == "__main__":
    import os
    import sys
    dir = 'tests/'
    start_time = time.time()
    if len(sys.argv) == 2:
        run_test(BASE_URL, dir + sys.argv[1] + '.json')
    else:
        files = os.listdir(dir)
        for filename in files:
            filepath = dir + filename
            if not os.path.isdir(filepath):
                run_test(BASE_URL, filepath)
#    print time.time() - start_time
