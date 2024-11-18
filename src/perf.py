from collections import deque
import sys
from jsonpickle import encode, decode
import time
import logging as l

from diff_codebase import *
from constraint_evaluator import *
from simple_interpreter import set_should_log
from main import eval_codebase
from symbolic_interpreter import SymbolicInterpreter
import pandas as pd

def perf():
    # if len(sys.argv) != 2:
    #     print("Please call with the codebase you want to run")
    #     exit()
    codebases = []
    if len(sys.argv) > 1:
        codebases = [sys.argv[1]]
    else:
        codebases = all_codebases()

    set_should_log(False)
    repetitions = 100
    results = []
    for i in range(repetitions):
        result = DeltaResult()
        for codebase in codebases:
            delta = eval_codebase(codebase, True)
            result.add_time(delta)
        results.append(result)
    
    # frame = pd.DataFrame.from_dict(results)
    frame = pd.DataFrame(results)
    print(frame.describe())

    print("all tests:", delta.entire_prev_run)
    print("necessary tests:", delta.entire_next_run)
    print("delta:", json.dumps(delta.times()))

if __name__ == '__main__':
    perf()
