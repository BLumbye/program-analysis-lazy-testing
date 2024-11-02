from src.common import *

def test_code_loads_classes():
    codebase = load_codebase("constant_becomes_equal", True)
    assert codebase.get_class("Simple") != None

def test_find_simple_test():
    codebase = load_codebase("constant_becomes_equal", True)
    assert any(x["name"] == "simpleTest" for x in codebase.get_tests()["Simple"])

def test_find_method_A():
    codebase = load_codebase("constant_becomes_equal", True)
    assert codebase.get_method("Simple", "A", [])

