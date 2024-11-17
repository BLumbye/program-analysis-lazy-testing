import pytest
from jpamb_util import *
from collections import deque
from common.codebase import Codebase
from common.common import constant_name
from common.expressions import ArrayExpr
from symbolic_interpreter import SymbolicInterpreter, Method

def add_expr(case: Case, local, idx):
    if type(local) is list:
        return (local, ArrayExpr(
            array = list(map(lambda ls: add_expr(case, ls, idx)[1], local)),
            size = add_expr(case, len(local), idx)[1]
        ))
    else:
        return (local, constant_name(str(f"input:{chr(97 + idx)}:{local}"), case.class_name, case.name))

class TestSymbolicInterpreter:

    @pytest.mark.parametrize("codebase", [load_jpamb_suite()])
    @pytest.mark.parametrize("case", prepare_cases())
    def test_jpamb_suite(self, codebase: Codebase, case: Case):
        bytecode = codebase.get_method(case.class_name, case.name, None)["code"]["bytecode"] # TODO: handle argument overloading
        expr_locals = [ add_expr(case, local, i) for i, local in enumerate(case.locals) ]
        stack = deque([Method(case.class_name, case.name, bytecode, expr_locals, deque(), 0)])
        result = SymbolicInterpreter(codebase, stack).interpret(limit=45000)
        expected_result = JPAMB_EXPECTED_RESULTS[case.id]
        assert result.test_name == case.name
        assert result.status == case.response
        assert set(result.depends_on_methods) == set(expected_result.depends_on_methods)

        if (case.id not in [57, 29, 28, 22, 19, 18, 17, 16, 15]): #TODO: missing cases (jpamb_util.py)
            assert set(result.depends_on_constants) == set(expected_result.depends_on_constants)
            assert result.constraints == expected_result.constraints
            assert result.cache_size == expected_result.cache_size
