import operator
from typing import Optional

from src.common import *

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

UNARY_OP = {
    UnaryOp.NEG: operator.neg,
    UnaryOp.NOT: operator.not_
}

def satisfies_constraints(constraints: list[Constraint], next: EntitySnapshot) -> bool:
    all(constraints, lambda c: evaluate_expr(c.expr, next.constants, [None] * c.cache_size))

def evaluate_expr(e: Expr, constants: dict[str, int], cache: list[Optional[bool | int]]) -> bool | int:
    match e:
        case BinaryExpr(): return evaluate_binary(e, constants, cache)
        case UnaryExpr(): return evaluate_unary(e, constants, cache)
        case Value(): return evaluate_value(e, constants)
        case e: raise ValueError(f"Unsupported expression: {e}")

def evaluate_binary(e: BinaryExpr, constants: dict[str, int], cache: list[Optional[bool | int]]) -> bool | int:
    if not cache[e.cache_id]:

        if (op := BINARY_OP.get(e.operator)) is not None:
            left = evaluate_expr(e.left, constants, cache)
            right = evaluate_expr(e.right, constants, cache)
            cache[e.cache_id] = op(left, right)
        else:
            raise ValueError(f"Unsupported binary operator: {e.operator}")
   
    return cache[e.cache_id]

def evaluate_unary(e: UnaryExpr, constants: dict[str, int], cache: list[Optional[bool | int]]) -> bool | int:
    if not cache[e.cache_id]:

        if (op := UNARY_OP.get(e.operator)) is not None:
            arg = evaluate_expr(e.arg, constants, cache)
            cache[e.cache_id] = op(arg)
        else:
            raise ValueError(f"Unsupported unary operator: {e.operator}")
    
    return cache[e.cache_id]

def evaluate_value(e: Value, constants: dict[str, int]) -> int:
    match e.kind:
        case ValueKind.CONST:
            if (v := constants.get(e.value)) is not None:
                return v
            raise ValueError(f"Undefined constant: {e.value}")
        
        case ValueKind.IMMED:
            return e.value
        
        case kind:
            raise ValueError(f"Unsupported value kind: {kind}")
