from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
import operator

@dataclass(frozen=True, eq=True)
class BinaryExpr:
    left: Expr
    operator: BinaryOp
    right: Expr
    cache_id: int # a unique id [0-n], so we can cache part of the computation 

@dataclass
class ArrayExpr:
    array: list[Expr]
    size: Expr

Expr = BinaryExpr | ArrayExpr | str # str is a constant_name

class BinaryOp(str, Enum):
    EQ = "==",
    NE = "!=",
    LT = "<",
    GE = ">=",
    GT = ">",
    LE = "<=",

    ADD = "+",
    SUB = "-",
    MUL = "*",
    DIV = "/",
    REM = "%"

BINARY_OPERATION = {
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

IF_CONDITION_HANDLERS = {
    "eq" : (lambda x, y: (BINARY_OPERATION[BinaryOp.EQ](x,y), BinaryOp.EQ)),
    "ne" : (lambda x, y: (BINARY_OPERATION[BinaryOp.NE](x,y), BinaryOp.NE)),
    "lt" : (lambda x, y: (BINARY_OPERATION[BinaryOp.LT](x,y), BinaryOp.LT)),
    "ge" : (lambda x, y: (BINARY_OPERATION[BinaryOp.GE](x,y), BinaryOp.GE)),
    "gt" : (lambda x, y: (BINARY_OPERATION[BinaryOp.GT](x,y), BinaryOp.GT)),
    "le" : (lambda x, y: (BINARY_OPERATION[BinaryOp.LE](x,y), BinaryOp.LE)),
}

BINARY_OPERATION_HANDLERS = {
    "add" : (lambda x, y: (BINARY_OPERATION[BinaryOp.ADD](x,y), BinaryOp.ADD)),
    "sub" : (lambda x, y: (BINARY_OPERATION[BinaryOp.SUB](x,y), BinaryOp.SUB)),
    "mul" : (lambda x, y: (BINARY_OPERATION[BinaryOp.MUL](x,y), BinaryOp.MUL)),
    "div" : (lambda x, y: (BINARY_OPERATION[BinaryOp.DIV](x,y), BinaryOp.DIV)),
    "rem" : (lambda x, y: (BINARY_OPERATION[BinaryOp.REM](x,y), BinaryOp.REM)),
}
