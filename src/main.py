from collections import deque
import sys
from jsonpickle import encode, decode

from diff_codebase import *
from constraint_evaluator import *
from interpreter import SimpleInterpreter, Method


def main():
    if len(sys.argv) != 2:
        print("Please call with the codebase you want to run")
        exit()

    # Load codebase before and after a change
    codebase_path = code_base_path(sys.argv[1])
    prev_codebase = load_decompiled(codebase_path, False)
    next_codebase = load_decompiled(codebase_path, True)

    # Initial test run
    prev_snapshot = codebase_snapshot(prev_codebase)
    prev_saved_result = SavedResult(prev_snapshot)
    run_tests(prev_saved_result, set(prev_codebase.all_test_names()), prev_codebase)

    # Save and restore JSON
    prev_saved_result = save_and_restore(codebase_path, prev_saved_result)

    # Incremental test run
    next_snapshot = codebase_snapshot(next_codebase)
    diff = diff_snapshots(prev_snapshot, next_snapshot)
    new_tests = tests_to_be_rerun(prev_saved_result, next_snapshot, diff)
    next_saved_result = SavedResult(next_snapshot)
    # print("rerunning tests:", new_tests)
    run_tests(next_saved_result, new_tests, next_codebase)

#TODO: lookup based on test
def run_tests(saved_result: SavedResult, required_tests: set[str], codebase : CodeBase) -> None:
    for class_name, tests in codebase.get_tests().items():
        for test in tests:
            # TODO: interpret
            # create savedResult based on all interpret results
            # 
            full_test_name = function_name(class_name, test["name"])
            if full_test_name not in required_tests:
                continue

            result = simple_test(class_name, test, codebase)
            saved_result.tests[full_test_name] = result
            for dependency in result.depends_on_functions:
                saved_result.entity_changes_tests.setdefault(dependency, []).append(full_test_name)

            for dependency in result.depends_on_constants:
                saved_result.entity_changes_tests.setdefault(dependency, []).append(full_test_name)
            # saved_result.entity_changes_tests
            # saved_result[function_name(class_name, test["name"])] = None
            # TODO: update snapshot.entity_changes_tests 

def simple_test(class_name: str, test: object, codebase: CodeBase) -> InterpretResult:
    interpreter = SimpleInterpreter(
        codebase=codebase,
        method_stack=deque([Method(test["name"], test["code"]["bytecode"], [], [], 0)])
    )

    # Step through the program and build the dependency graph
    # TODO: Handle other invokations than static
    limit = 1000
    constant_dependencies = set()
    function_dependencies = set(*[function_name(class_name, test["name"])])
    while interpreter.step_count < limit and interpreter.done is None:
        next = interpreter.method_stack[-1].bytecode[interpreter.method_stack[-1].pc]
        if next["opr"] == "push":
            constant_dependencies.add(constant_name(str(next["offset"]), class_name, test["name"]))
        if next["opr"] == "invoke" and next["access"] == "static":
            function_dependencies.add(function_name(next["method"]["ref"]["name"], next["method"]["name"]))
        interpreter.step()

    result = InterpretResult(
        test_name=function_name(class_name, test["name"]),
        status=interpreter.done,
        depends_on_constants=list(constant_dependencies),
        depends_on_functions=list(function_dependencies),
        constraints=[],
        cache_size=0
    )
    return result

def tests_to_be_rerun(prev: SavedResult, next: EntitySnapshot, diff: SnapshotDiff) -> set[str]:
    to_be_run = set() # is the test already supposed to be rerun
    has_been_evaluated = set() # have the constraints been evaluated

    for method in diff.changed_methods:
        if method in prev.entity_changes_tests:
            tests = prev.entity_changes_tests[method]
            to_be_run.add(*tests)
    
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
