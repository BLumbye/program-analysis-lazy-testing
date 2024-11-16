import pytest
from jpamb_util import *
from collections import deque
from src.common.codebase import Codebase
from src.common.common import constant_name
from src.symbolic_interpreter import SymbolicInterpreter, Method

def add_expr(case: Case, locals):
    if type(locals) is list:
        return list(map(lambda ls: add_expr(case, ls), locals))
    else:
        return (locals, constant_name(str(f"input:{locals}"), case.class_name, case.name))

class TestSymbolicInterpreter:

    @pytest.mark.parametrize("codebase", [load_jpamb_suite()])
    @pytest.mark.parametrize("case", prepare_cases())
    def test_jpamb_suite(self, codebase: Codebase, case: Case):
        if case.class_name != "jpamb/cases/Arrays" and not case.name in ["allPrimesArePositive"]: #TODO: missing array support

            bytecode = codebase.get_method(case.class_name, case.name, None)["code"]["bytecode"] # TODO: handle argument overloading
            stack = deque([Method(case.class_name, case.name, bytecode, add_expr(case, case.locals), deque(), 0)])
            result = SymbolicInterpreter(codebase, stack).interpret(limit=45000)
            expected_result = JPAMB_EXPECTED_RESULTS[case.id]
            assert result.test_name == case.name
            assert result.status == case.response
            assert set(result.depends_on_methods) == set(expected_result.depends_on_methods)
            # assert result.depends_on_constants == expected_result.depends_on_constants
            # assert result.constraints == expected_result.constraints
            # assert result.cache_size == expected_result.cache_size
