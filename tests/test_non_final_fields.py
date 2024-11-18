from common.codebase import *
from simple_interpreter import Method, SimpleInterpreter

def test_codebase_loads_fields():
    codebase = load_codebase("non_final_fields", True)
    assert codebase.get_fields()["Fields"]["A"] == 3

def test_interpreter():
    codebase = load_codebase("non_final_fields", True)
    interpreter = SimpleInterpreter(codebase, deque([Method("Simple", "unchanged", codebase.get_method(
        "Simple", "unchanged", [])["code"]["bytecode"], [], deque(), 0)]))
    result = interpreter.interpret()
    assert result.status == "ok"

