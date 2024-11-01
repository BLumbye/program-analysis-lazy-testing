from __future__ import annotations
from hypothesis import given, settings

from src.common import *
from src.constraint_evaluator import *
from tests.constraint_generator import expr_gen

class TestConstraintEvaluator:

    @settings(max_examples = 1000)
    @given(expr_gen())
    def test_expr(self, args):
        try:
            expr, constants, cache = args
            print(expr_to_string(expr))
            assert evaluate_expr(expr, constants, cache) == eval(expr_to_string(expr), constants)
        except ZeroDivisionError: #TODO:
            assert True

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

PY_UNARY_OP = {
    UnaryOp.NEG: "-",
    UnaryOp.NOT: "not"
}

def expr_to_string(e: Expr) -> str:
    match e:
        case BinaryExpr(): return binary_to_string(e)
        case UnaryExpr(): return unary_to_string(e)
        case Value(): return value_to_string(e)
        case e: raise ValueError(f"Unsupported expression: {e}")

def binary_to_string(e: BinaryExpr) -> str:
    if (op := PY_BINARY_OP.get(e.operator)) is not None:
        return f"({expr_to_string(e.left)} {op} {expr_to_string(e.right)})"
    raise ValueError(f"Unsupported binary operator: {e.operator}")

def unary_to_string(e: UnaryExpr) -> str:
    if (op := PY_UNARY_OP.get(e.operator)) is not None:
        return f"({op} {expr_to_string(e.arg)})"
    raise ValueError(f"Unsupported unary operator: {e.operator}")

def value_to_string(e: Value) -> str:
    match e.kind:
        case ValueKind.CONST: return e.value
        case ValueKind.IMMED: return str(e.value)
        case kind: raise ValueError(f"Unsupported value kind: {kind}")
