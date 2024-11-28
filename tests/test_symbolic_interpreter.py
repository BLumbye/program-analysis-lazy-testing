import pytest
from jpamb_util import *
from collections import deque
from common.codebase import Codebase
from common.common import constant_name
from common.expressions import ArrayExpr
from symbolic_interpreter import SymbolicInterpreter, Method

def add_expr(case: Case, local, arg_idx, arr_ident):
    if type(local) is list:
        return (local, ArrayExpr(
            size = add_expr(case, len(local), arg_idx, "size")[1],
            array = [ add_expr(case, local_elem, arg_idx, str(arr_idx))[1] 
                        for arr_idx, local_elem in enumerate(local) ]
        ))
    else:
        const_name = constant_name(
            f"input:{chr(97 + arg_idx)}{(":" + arr_ident) if arr_ident else ""}:{local}", 
            case.class_name, 
            case.name
        )
        return (local, const_name)

class TestSymbolicInterpreter:

    @pytest.mark.parametrize("codebase", [load_jpamb_suite()])
    @pytest.mark.parametrize("case", prepare_cases())
    def test_jpamb_suite(self, codebase: Codebase, case: Case):
        bytecode = codebase.get_method(case.class_name, case.name, None)["code"]["bytecode"]
        expr_locals = [ add_expr(case, local, idx, None) for idx, local in enumerate(case.locals) ]
        stack = deque([Method(case.class_name, case.name, bytecode, expr_locals, deque(), 0)])
        result = SymbolicInterpreter(codebase, stack).interpret(limit=45000)
        expected_result = JPAMB_EXPECTED_RESULTS[case.id]
        assert result.test_name == case.name
        assert result.status == case.response
        assert set(result.depends_on_methods) == set(expected_result.depends_on_methods)

        if (case.id not in [57, 29, 28, 22, 19, 18, 17, 16, 15]):
            assert set(result.depends_on_constants) == set(expected_result.depends_on_constants)
            assert result.constraints == expected_result.constraints
            assert result.cache_size == expected_result.cache_size
