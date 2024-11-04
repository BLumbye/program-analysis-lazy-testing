import sys
from jsonpickle import encode, decode

from diff_codebase import *
from constraint_evaluator import *

def main() -> None:
    if len(sys.argv) < 1:
        print("Please call with the codebase you want to run")
        exit()

    # Load codebase before and after a change
    codebase_path = code_base_path(sys.argv[1])
    prev_codebase = load_decompiled(codebase_path, False)
    next_codebase = load_decompiled(codebase_path, True)

    # Initial test run
    prev_snapshot = codebase_snapshot(prev_codebase)
    prev_saved_result = SavedResult(prev_snapshot)
    run_tests(prev_saved_result, prev_codebase.get_tests().items(), prev_codebase)

    # Save and restore JSON
    prev_saved_result = save_and_restore(codebase_path, prev_saved_result)

    # Incremental test run
    next_snapshot = codebase_snapshot(next_codebase)
    diff = diff_snapshots(prev_snapshot, next_snapshot)
    new_tests = tests_to_be_rerun(prev_saved_result, next_snapshot, diff)
    next_saved_result = SavedResult(next_snapshot)
    run_tests(next_saved_result, new_tests, next_codebase)

def run_tests(saved_result: SavedResult, tests: list[tuple[str, str]], codebase : CodeBase) -> None:
    for class_name, test in tests:
        # TODO: interpret
        # TODO: update saved_result.tests 
        saved_result[function_name(class_name, test["name"])] = None
        # TODO: update saved_result.entity_changes_tests 

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

def save_and_restore(codebase_path, prev_saved_result):
    json_path = os.path.join(codebase_path, "saved_result.json")
    with open(json_path, "w") as file:
        file.write(encode(prev_saved_result))

    with open(json_path, "r") as file:
        return decode(file.read())
  
if __name__ == '__main__':
    main()
