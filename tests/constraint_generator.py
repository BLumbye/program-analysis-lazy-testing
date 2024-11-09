from hypothesis import strategies as st
import keyword
from src.common.binary_expression import *

int_gen = st.integers(-1000, 1000)

py_constant_gen = st.text(
    "abcdefghijklmnopqrstuvwxyz",
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
        | binary_generator(constants, cache)
    )

@st.composite
def binary_generator(draw, constants: dict[str, int], cache: list[None]):
    left = draw(pick_node(constants, cache))
    right = draw(pick_node(constants, cache))
    op = draw(st.sampled_from(BinaryOp))
    cache.append(None)
    return BinaryExpr(left, op, right, len(cache) - 1)

@st.composite
def value_generator(draw, constants: dict[str, int]) -> int:
    value = draw(py_constant_gen)
    constants[value] = draw(int_gen)
    return value
