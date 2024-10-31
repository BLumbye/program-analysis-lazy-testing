import os
import sys
import json

from diff_codebase import *
from constraint_verifier import *

# arg: (codebase)
# run dynamic on previous
# syntactic analysis on next
# maybe constraints
# dynamic on next

def run_tests(saved_result: SavedResult, tests: list[tuple[str, str]], codebase : CodeBase) -> None:
    for class_name, test in tests:
        # TODO: interpret
        # create savedResult based on all interpret results
        saved_result[function_name(class_name, test["name"])] = None
        # TODO: update snapshot.entity_changes_tests 
    
def main():
    if sys.argv != 1:
        print("Please call with the codebase you want to run")
        exit()

    # Load codebase before and after a change
    codebase_path = code_base_path(sys.args[0])
    codebase_prev = load_decompiled(codebase_path, False)
    codebase_next = load_decompiled(codebase_path, True)

    # Initial test run
    prev_snapshot = codebase_snapshot(codebase_prev)
    prev_saved_result = SavedResult()
    prev_saved_result.snapshot = prev_snapshot
    run_tests(codebase_prev.get_tests().items())

    # TODO: highly theoretical save to JSON

    # Incremental test run
    next_snapshot = codebase_snapshot(codebase_next)
    diff = diff_snapshots(prev_snapshot, next_snapshot)
    new_tests = tests_to_be_rerun(prev_saved_result, next_snapshot, diff)
    next_saved_result = SavedResult()
    next_saved_result.snapshot = next_snapshot
    run_tests(next_saved_result, new_tests, codebase_next)

def all_file_paths(dir: str):
    paths = []
    for root, _, filenames in os.walk(dir):
        for name in filenames:
            paths.append((os.path.splitext(name)[0], os.path.join(root, name)))
    
    return paths

def code_base_path(codebase: str):
    return os.path.join(os.path.dirname(__file__), "..", "codebases", codebase)

def load_decompiled(codebase_dir: str, is_next: bool) -> CodeBase:
    bytecode = dict()
    dir = "next" if is_next else "previous"
    for name, file_path in all_file_paths(os.path.join(codebase_dir, dir, "decompiled")):
        with open(file_path, 'r') as file:
            bytecode[name] = json.load(file)

    return CodeBase(bytecode)

def tests_to_be_rerun(prev: SavedResult, next: EntitySnapshot, diff: SnapshotDiff) -> set[str]:
    to_be_run = set() # is the test already supposed to be rerun
    has_been_evaluated = set() # have the constraints been evaluated

    for method in diff.changed_methods:
        tests = prev.entity_changes_tests[method]
        to_be_run.add(*tests)
    
    for constant in diff.changed_constants:
        tests = prev.entity_changes_tests[constant]
        for test in tests:
            if test not in to_be_run and test not in has_been_evaluated:
                constraints = prev.tests[test].constraints
                has_been_evaluated.add(test)
                if not verify_constraints(constraints, next):
                    to_be_run.add(test)
    
# print(json.dumps(load_decompiled(code_base_path("constant_becomes_equal", True))))
# decompiled = load_decompiled(code_base_path("constant_becomes_equal"), True)
# print(calc_snapshot(decompiled))
if __name__ == '__main__':
    main()
