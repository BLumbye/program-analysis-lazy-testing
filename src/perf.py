from collections import deque
import sys
from jsonpickle import encode, decode
import time
import logging as l

from diff_codebase import *
from constraint_evaluator import *
from simple_interpreter import SimpleInterpreter, Method
from main import eval_codebase
from symbolic_interpreter import SymbolicInterpreter

def perf():
    # if len(sys.argv) != 2:
    #     print("Please call with the codebase you want to run")
    #     exit()
    codebases = []
    if len(sys.argv) > 1:
        codebases = [sys.argv[1]]
    else:
        codebases = all_codebases()

    l.disable(l.DEBUG) 
    
    delta = eval_codebase(sys.argv[1], True)
    print("all tests:", delta.entire_prev_run())
    print("necessary tests:", delta.entire_next_run())
    print("delta:", json.dumps(delta.times()))

if __name__ == '__main__':
    perf()
