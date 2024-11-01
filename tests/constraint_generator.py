from hypothesis import strategies as st
import keyword
from src.common import *

int_gen = st.integers(-1000, 1000)

py_constant_gen = st.text(
    "abcdefghijklmnopqrstuvwxyz_",
    min_size=1, 
    max_size=30
).filter(lambda c: c not in keyword.kwlist)

@st.composite
def expr_gen(draw) -> tuple[Expr, dict[str, int], list[None]]:
    constants = {}
    cache = []
    return (draw(pick_node(constants, cache)), constants, cache)

def pick_node(constants: dict[str, int], cache: list[None]):
    return st.deferred(lambda: # TODO: assign different probabilities
          value_generator(constants) 
        | unary_generator(constants, cache) 
        | binary_generator(constants, cache)
    )

@st.composite
def binary_generator(draw, constants: dict[str, int], cache: list[None]):
    left = draw(pick_node(constants, cache))
    right = draw(pick_node(constants, cache))
    op = draw(st.sampled_from(BinaryOp))
    cache.append(None)
    return BinaryExpr(left, right, op, len(cache) - 1)

@st.composite
def unary_generator(draw, constants: dict[str, int], cache: list[None]):
    arg = draw(pick_node(constants, cache))
    op = draw(st.sampled_from(UnaryOp))
    cache.append(None)
    return UnaryExpr(arg, op, len(cache) - 1)

@st.composite
def value_generator(draw, constants: dict[str, int]) -> Value:
    kind = draw(st.sampled_from(ValueKind))
    match kind:
        case ValueKind.CONST:
            value = draw(py_constant_gen)
            constants[value] = draw(int_gen)
        case ValueKind.IMMED:
            value = draw(int_gen)

    return Value(kind, value)
