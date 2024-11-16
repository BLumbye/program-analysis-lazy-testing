import pytest
from jpamb_util import Case, load_jpamb_suite, prepare_cases
from collections import deque
from src.common.codebase import Codebase
from src.simple_interpreter import SimpleInterpreter, Method

class TestSimpleInterpreter:

    @pytest.mark.parametrize("codebase", [load_jpamb_suite()])
    @pytest.mark.parametrize("case", prepare_cases())
    def test_jpamb_suite(self, codebase: Codebase, case: Case):
        bytecode = codebase.get_method(case.class_name, case.name, None)["code"]["bytecode"] # TODO: handle argument overloading
        stack = deque([Method(case.class_name, case.name, bytecode, case.locals, deque(), 0)])
        result = SimpleInterpreter(codebase, stack).interpret(limit=45000)
        assert result.status == case.response
