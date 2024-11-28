from collections import deque
import sys
from jsonpickle import encode, decode
import time

from diff_codebase import *
from constraint_evaluator import *
from simple_interpreter import SimpleInterpreter, Method, set_should_log
from symbolic_interpreter import SymbolicInterpreter

def main():
    if len(sys.argv) < 2:
        print("please call with ")
        print("main {codebase} [interpreter]")
        print(" - {codebase} is the name of the code base")
        print(" - [codebase] optionally specify the interpreter as dynamic or symbolic, default is symbolic")
        print("example call:")
        print("python src/main.py constant_becomes_equal dynamic")
        exit()
    # So why not just pass a function that calls either interpreter?
    # This is because other parts of the program might need to react to the interpreter (might be a wrong decision)
    symbolic_interpreter = True
    if(len(sys.argv) >= 3):
        symbolic_interpreter = sys.argv[2] == "symbolic"
    
    delta = eval_codebase(sys.argv[1], symbolic_interpreter)
    print("all tests:", delta.t_run_all_tests)
    print("necessary tests:", delta.t_run_necessary_tests)
    print("actual", delta.new_tests)
    print("prev constants", delta.prev_snapshot.constants)
    print("next constants", delta.next_snapshot.constants)
    print("next constants", delta.prev_saved_result.tests)


def timer(fun):
    start = time.perf_counter_ns()
    result = fun()
    end = time.perf_counter_ns()
    return result, (end - start) / 1000

def eval_codebase(codebase_name: str, use_symbolic_interpreter:bool) -> DeltaResult:
    sys.setrecursionlimit(10000000) # handle issues related to recursion limit
    result = DeltaResult()

    # Load codebase before and after a change
    codebase_path = code_base_path(codebase_name)
    result.prev_codebase, result.t_prev_codebase = timer(lambda: load_decompiled(codebase_path, False))
    result.next_codebase, result.t_next_codebase = timer(lambda: load_decompiled(codebase_path, True))

    # Initial test run
    result.prev_snapshot, result.t_prev_snapshot = timer(lambda: codebase_snapshot(result.prev_codebase))
    result.prev_saved_result, result.t_prev_saved_result = timer(lambda: SavedResult(result.prev_snapshot))
    _, result.t_run_all_tests = timer(lambda:run_tests(result.prev_saved_result, set(result.prev_codebase.all_test_names()), result.prev_codebase, use_symbolic_interpreter))

    # Save and restore JSON
    result.prev_saved_result, result.t_save_and_restore = timer(lambda: save_and_restore(codebase_path, result.prev_saved_result))
    
    # Incremental test run
    result.next_snapshot, result.t_next_snapshot = timer(lambda: codebase_snapshot(result.next_codebase))
    result.diff, result.t_diff = timer(lambda:diff_snapshots(result.prev_snapshot, result.next_snapshot))
    result.new_tests, result.t_new_tests = timer(lambda:tests_to_be_rerun(result.prev_saved_result, result.next_snapshot, result.diff))
    result.next_saved_result, result.t_next_saved_result = timer(lambda:SavedResult(result.next_snapshot))

    _, result.t_run_necessary_tests = timer(lambda: run_tests(result.next_saved_result, result.new_tests, result.next_codebase, use_symbolic_interpreter))

    return result

#TODO: lookup based on test
def run_tests(saved_result: SavedResult, required_tests: set[str], codebase : Codebase, use_symbolic_interpreter: bool) -> None:
    for class_name, tests in codebase.get_tests().items():
        for test in tests:
            full_test_name = abs_method_name(class_name, test["name"])
            if full_test_name not in required_tests:
                continue

            stack = deque([Method(class_name, test["name"], test["code"]["bytecode"], [], deque(), 0)])
            
            result = SymbolicInterpreter(codebase, stack).interpret() if use_symbolic_interpreter else simple_test(codebase, stack, saved_result.snapshot, full_test_name)
            # result = SymbolicInterpreter(codebase, stack).interpret()
            
            saved_result.tests[full_test_name] = result
            for dependency in result.depends_on_methods:
                saved_result.entity_changes_tests.setdefault(dependency, []).append(full_test_name)

            for dependency in result.depends_on_constants:
                saved_result.entity_changes_tests.setdefault(dependency, []).append(full_test_name)

def simple_test(codebase: Codebase, stack: SymbolicInterpreter, snapshot: EntitySnapshot, full_test_name: str) -> InterpretResult:
    result = SimpleInterpreter(codebase, stack).interpret()
    # Problem: We have to track the variables we interact with, because constants are not part of the method hash
    for constant_name in result.depends_on_constants:
        constant_value = snapshot.constants[constant_name]
        result.constraints.append(BinaryExpr(constant_name, BinaryOp.EQ, constant_value, result.cache_size)) # for now we add all constants as dependencies. Which is bad because all tests break without reason
        result.cache_size += 1
    return result
    
def tests_to_be_rerun(prev: SavedResult, next: EntitySnapshot, diff: SnapshotDiff) -> set[str]:
    to_be_run = set() # is the test already supposed to be rerun
    has_been_evaluated = set() # have the constraints been evaluated

    # print("changed methods",diff.changed_constants)
    for method in diff.changed_methods:
        if method in prev.entity_changes_tests:
            tests = prev.entity_changes_tests[method]
            for test in tests:
                to_be_run.add(test)
    
    
    for constant in diff.changed_constants:
        if constant in prev.entity_changes_tests:
            tests = prev.entity_changes_tests[constant]
            for test in tests:
                if test not in to_be_run and test not in has_been_evaluated:
                    if not satisfies_constraints(prev.tests[test], next):
                        to_be_run.add(test)
                    has_been_evaluated.add(test)
    return to_be_run

def save_and_restore(codebase_path, prev_saved_result):
    json_path = os.path.join(codebase_path, "saved_result.json")
    with open(json_path, "w") as file:
        file.write(encode(prev_saved_result))

    with open(json_path, "r") as file:
        return decode(file.read())

if __name__ == '__main__':
    main()
