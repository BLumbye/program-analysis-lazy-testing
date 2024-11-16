from hypothesis import given, settings

from src.common.binary_expression import *
from src.constraint_evaluator import *
from constraint_generator import expr_gen

class TestConstraintEvaluator:

    @settings(max_examples = 10)
    @given(expr_gen())
    def test_expr(self, args):
        try:
            expr, constants, cache = args
            assert evaluate_expr(expr, constants, cache) == eval(expr_to_string(expr), constants)
        except ZeroDivisionError:
            assert True # Invalid expression

PY_BINARY_OP = {
    BinaryOp.EQ: "==",
    BinaryOp.NE: "!=",
    BinaryOp.LT: "<",
    BinaryOp.GE: ">=",
    BinaryOp.GT: ">",
    BinaryOp.LE: "<=",

    BinaryOp.ADD: "+",
    BinaryOp.SUB: "-",
    BinaryOp.MUL: "*",
    BinaryOp.DIV: "//",
    BinaryOp.REM: "%",
}

def expr_to_string(e: Expr) -> str:
    return e if type(e) is str else binary_to_string(e)

def binary_to_string(e: BinaryExpr) -> str:
    if (op := PY_BINARY_OP.get(e.operator)) is None:
        raise ValueError(f"Unsupported binary operator: {e.operator}")
    return f"({expr_to_string(e.left)} {op} {expr_to_string(e.right)})"
