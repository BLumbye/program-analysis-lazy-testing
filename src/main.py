import sys

from diff_codebase import *
from constraint_evaluator import *

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
    # TODO: highly theoretical load to JSON

    # Incremental test run
    next_snapshot = codebase_snapshot(codebase_next)
    diff = diff_snapshots(prev_snapshot, next_snapshot)
    new_tests = tests_to_be_rerun(prev_saved_result, next_snapshot, diff)
    next_saved_result = SavedResult()
    next_saved_result.snapshot = next_snapshot
    run_tests(next_saved_result, new_tests, codebase_next)

def run_tests(saved_result: SavedResult, tests: list[tuple[str, str]], codebase : CodeBase) -> None:
    for class_name, test in tests:
        # TODO: interpret
        # create savedResult based on all interpret results
        saved_result[function_name(class_name, test["name"])] = None
        # TODO: update snapshot.entity_changes_tests 

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
                if not satisfies_constraints(prev.tests[test], next):
                    to_be_run.add(test)
                has_been_evaluated.add(test)
    
if __name__ == '__main__':
    main()
