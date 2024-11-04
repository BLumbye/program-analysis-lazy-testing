import operator
from typing import Optional

from common import *

BINARY_OP = {
    BinaryOp.EQ: operator.eq,
    BinaryOp.NE: operator.ne,
    BinaryOp.LT: operator.lt,
    BinaryOp.GE: operator.ge,
    BinaryOp.GT: operator.gt,
    BinaryOp.LE: operator.le,

    BinaryOp.ADD: operator.add,
    BinaryOp.SUB: operator.sub,
    BinaryOp.MUL: operator.mul,
    BinaryOp.DIV: operator.floordiv, # as we only support integers
    BinaryOp.REM: operator.mod,
}

def satisfies_constraints(prev: InterpretResult, next: EntitySnapshot) -> bool:
    cache = [None] * prev.cache_size
    all(prev.constraints, lambda c: evaluate_expr(c.expr, next.constants, cache))

def evaluate_expr(e: Expr, constants: dict[str, int], cache: list[Optional[bool | int]]) -> bool | int:
    if type(e) is str:
        return evaluate_value(e, constants)
    else:
        # assumes it is a binary expression
        return evaluate_binary(e, constants, cache)

def evaluate_binary(e: BinaryExpr, constants: dict[str, int], cache: list[Optional[bool | int]]) -> bool | int:
    if not cache[e.cache_id]:

        if (op := BINARY_OP.get(e.operator)) is not None:
            left = evaluate_expr(e.left, constants, cache)
            right = evaluate_expr(e.right, constants, cache)
            cache[e.cache_id] = op(left, right)
        else:
            raise ValueError(f"Unsupported binary operator: {e.operator}")
   
    return cache[e.cache_id]

def evaluate_value(e: str, constants: dict[str, int]) -> int:
    if (v := constants.get(e)) is not None:
        return v
    raise ValueError(f"Undefined constant: {e}")
