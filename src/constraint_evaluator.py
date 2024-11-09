from typing import Optional
from common.results import *
from common.binary_expression import *

def satisfies_constraints(prev: InterpretResult, next: EntitySnapshot) -> bool:
    cache = [None] * prev.cache_size
    # print(prev.constraints)
    return all([evaluate_expr(e, next.constants, cache) for e in prev.constraints])
    # for e in prev.constraints:
    #     if not evaluate_expr(e, next.constants, cache):
    #         # print("$$$ failed expression", e)
    #         return False
        
    # return True

def evaluate_expr(e: Expr, constants: dict[str, int], cache: list[Optional[bool | int]]) -> bool | int:
    if type(e) is str:
        return evaluate_value(e, constants)
    else:
        # assumes it is a binary expression
        return evaluate_binary(e, constants, cache)

def evaluate_binary(e: BinaryExpr, constants: dict[str, int], cache: list[Optional[bool | int]]) -> bool | int:
    if not cache[e.cache_id]:

        if (op := BINARY_OPERATION.get(e.operator)) is not None:
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
