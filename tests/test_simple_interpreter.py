import pytest
from jpamb_util import *
from collections import deque
from common.codebase import Codebase
from simple_interpreter import SimpleInterpreter, Method

class TestSimpleInterpreter:

    @pytest.mark.parametrize("codebase", [load_jpamb_suite()])
    @pytest.mark.parametrize("case", prepare_cases())
    def test_jpamb_suite(self, codebase: Codebase, case: Case):
        bytecode = codebase.get_method(case.class_name, case.name, None)["code"]["bytecode"]
        stack = deque([Method(case.class_name, case.name, bytecode, case.locals, deque(), 0)])
        result = SimpleInterpreter(codebase, stack).interpret(limit=45000)
        expected_value = JPAMB_EXPECTED_RESULTS[case.id]
        assert result.test_name == case.name
        assert result.status == case.response
        assert set(result.depends_on_methods) == set(expected_value.depends_on_methods)
        if (case.id not in [57, 22, 19, 18, 17, 16, 15]):
            assert set(result.depends_on_constants) == set(expected_value.depends_on_constants)
