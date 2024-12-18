from src.common.codebase import *
from src.main import eval_codebase
from src.simple_interpreter import set_should_log
import pytest

def method_is_expected_to_be_run_again(method, should_run_key:str):
    return any(annotation["values"][should_run_key]["value"] == 1 for annotation in method["annotations"] if annotation["type"] =="utils/Test")
    

def get_expected_test_names(codebase: Codebase, should_run_key:str) -> set[str]:
    test_names = set()
    for c, tests in codebase.get_tests().items():
        for t in tests:
            if method_is_expected_to_be_run_again(t, should_run_key):
                test_names.add(abs_method_name(c, t["name"]))
    return test_names

def codebases_except_scratch() -> list[str]:
    codebases = all_codebases()
    codebases.remove("scratch")
    return codebases

@pytest.mark.parametrize("codebase_name", codebases_except_scratch())
def test_codebase_symbolic_reruns(codebase_name: str):
    print("codebase_name", codebase_name)
    set_should_log(False)
    delta = eval_codebase(codebase_name, True)
    expected_rerun_tests = get_expected_test_names(delta.prev_codebase, "shouldRunSymbolic")
    print("expected", expected_rerun_tests)
    print("actual", delta.new_tests)
    # print("prev constants", delta.prev_snapshot.constants)
    # print("next constants", delta.next_snapshot.constants)
    assert delta.new_tests == expected_rerun_tests

@pytest.mark.parametrize("codebase_name", codebases_except_scratch())
def test_codebase_dynamic_reruns(codebase_name: str):
    print("codebase_name", codebase_name)
    set_should_log(False)
    delta = eval_codebase(codebase_name, False)
    expected_rerun_tests = get_expected_test_names(delta.prev_codebase, "shouldRunDynamic")
    print("expected", expected_rerun_tests)
    print("actual", delta.new_tests)
    print("prev constants", delta.prev_snapshot.constants)
    print("next constants", delta.next_snapshot.constants)
    assert delta.new_tests == expected_rerun_tests