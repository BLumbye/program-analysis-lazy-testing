import json
from pathlib import Path
import re
from symbolic_interpret import SymbolicInterpreter
import sys, logging
import random

l = logging
l.basicConfig(level=logging.DEBUG, format="%(message)s") 
call = sys.argv
l.debug(call)

class MetodID:
    bytecode:list
    max_local:int
    param:None
    call:str

    def __init__(self,call):
        self.call = call

    def get_info(self):
        self.parse_call()
        return self.bytecode,self.max_local,self.param
    def parse_call(self):
        call = self.call[1].replace("'", "")
        call=call.replace("'", "")
        #'jpamb.cases.Simple.justReturn:()I'
        regex = re.compile(r"(?P<class_name>.+)\.(?P<method_name>.*)\:\((?P<params>.*)\)(?P<return>.*)")

        match = regex.search(call)
        info = match.groupdict()
        class_name = info['class_name'].replace(".","/")+(".json")
        file_path = Path("C:/Users/Mondk/Documents/GitHub/group34_program_analysis/decompiled")/class_name
        file_path=str(file_path).replace('\\','/')
        method_name = info['method_name']

        self.parse_file(file_path,method_name)
        self.param = info['params']
        

    def parse_file(self,file_path, method_name):
        self.bytecode =[]
        max_locals =0
        with open(file_path, 'r') as file:
            java_code = file.read()
            json_obj = json.loads(java_code)
            for i in json_obj['methods']:
                if i['name'] == method_name:
                    for c in i['code']['bytecode']:
                        self.bytecode.append(c)
                    max_locals=i['code']['max_locals']
                    break
        if len(self.bytecode) ==0:
            print('Error no bytecode for: ',method_name)
        self.max_local=max_locals
    def parse_param(self,s:str):

        if s == '()':
            return []
        # Handle boolean case
        if s== "'(true)'":
            return [True]
        elif s == "'(false)'":
            return [False]
        if s== '(true)':
            return [True]
        elif s == '(false)':
            return [False]
        
        # Handle list of integers case
        match = re.search(r'\((-?\d+(?:,\s*-?\d+)*)\)', s)
        l.debug(match)
        if match:
            # Split by commas and convert to integers
            return [int(x) for x in match.group(1).split(',')]
        l.debug(s)
        raise ValueError("Input string does not match expected format")

bytecode, max_locals, param = MetodID(call).get_info()



int_range = (-1000,1000)
bool_values = [True, False]


def make_child():
    if param == 'II':
            return [random.randint(*int_range), random.randint(*int_range)]
    if param == 'Z':
        return random.choice(bool_values)
    else:
        return random.randint(*int_range) 
    
l.debug(make_child())

interpreter = SymbolicInterpreter(bytecode,max_locals,make_child())

result = interpreter.interpret()

if result =='ok':
     print('ok;50%')
else:
     print(result+';100%')


