from src.common import *
from src.diff_codebase import *


#### ----- constant becomes equal ------- 
def test_find_SOME_CONSTANT():
    codebase = load_codebase("constant_becomes_equal", True)
    snapshot = codebase_snapshot(codebase)
    assert snapshot.constants[constant_name("SOME_CONSTANT", "Simple")] == 42
    
    
def test_find_inlineconstant():
    codebase = load_codebase("constant_becomes_equal", True)
    snapshot = codebase_snapshot(codebase)
    assert snapshot.constants[constant_name("9", "Simple", "simpleTest")] == 42
    
#### ----- constant becomes equal ------- 
def test_constant_changes_does_not_trigger_method_change():
    codebase_prev = load_codebase("detect_function_changes", False)
    codebase_next = load_codebase("detect_function_changes", True)
    snapshot_prev = codebase_snapshot(codebase_prev)
    snapshot_next = codebase_snapshot(codebase_next)
    diff = diff_snapshots(snapshot_prev, snapshot_next)
    
    assert function_name("Simple","testOnlyChangesInlineConstants") not in diff.changed_methods
    
def test_detect_changed_implementation():
    codebase_prev = load_codebase("detect_function_changes", False)
    codebase_next = load_codebase("detect_function_changes", True)
    snapshot_prev = codebase_snapshot(codebase_prev)
    snapshot_next = codebase_snapshot(codebase_next)
    diff = diff_snapshots(snapshot_prev, snapshot_next)
    
    assert function_name("Simple", "testChangesImplementation") in diff.changed_methods

def test_detect_changed_dependency_method():
    codebase_prev = load_codebase("detect_function_changes", False)
    codebase_next = load_codebase("detect_function_changes", True)
    snapshot_prev = codebase_snapshot(codebase_prev)
    snapshot_next = codebase_snapshot(codebase_next)
    diff = diff_snapshots(snapshot_prev, snapshot_next)
    print(diff.changed_methods)
    assert function_name("Simple", "C") in diff.changed_methods

def test_B_method_has_not_changed():
    codebase_prev = load_codebase("detect_function_changes", False)
    codebase_next = load_codebase("detect_function_changes", True)
    snapshot_prev = codebase_snapshot(codebase_prev)
    snapshot_next = codebase_snapshot(codebase_next)
    diff = diff_snapshots(snapshot_prev, snapshot_next)
    print(diff.changed_methods)
    assert function_name("Simple", "B") not in diff.changed_methods