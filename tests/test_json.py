from jsonpickle import decode, encode
from hypothesis import given, settings, strategies as st

from src.common.binary_expression import BinaryOp
from src.diff_codebase import *

class TestJson:

    @settings(max_examples = 100)
    @given(st.from_type(SavedResult)) #TODO: ensure less empty dicts?
    def test_prop_json(self, saved_result):
        assert saved_result == decode(encode(saved_result))

    def test_json(self):
        codebase = load_codebase("constant_becomes_equal", True)
        saved_result = SavedResult(codebase_snapshot(codebase))
        saved_result.entity_changes_tests = { "x" : "test", "y" : "test" }
        result = InterpretResult(
            "test", "done", 
            ["x", "y", "z"], ["f", "g", "h"], 
            [BinaryExpr(BinaryExpr("x", BinaryOp.ADD, "y", 0), BinaryOp.EQ, BinaryExpr("z", BinaryOp.SUB, "y", 1), 2)],
            2
        )
        saved_result.tests = { "test" : result }
        
        assert saved_result == decode(encode(saved_result))
