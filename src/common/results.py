from __future__ import annotations
from dataclasses import dataclass, field
from common.binary_expression import BinaryExpr
from common.common import CONST_ZERO, CONST_ASSERTION_DISABLED
from common.codebase import Codebase

# Note: result is written so it is able to be serialized
@dataclass
class InterpretResult:
    test_name: str
    status: str # The same status as JPAMB
    depends_on_methods: list[str]
    depends_on_constants: list[str]
    constraints: list[BinaryExpr]
    cache_size: int  # the number of unique cache ids

# The thing stored in JSON
@dataclass
class SavedResult:
    snapshot: EntitySnapshot
    entity_changes_tests: dict[str, list[str]] = field(default_factory=dict)
    tests: dict[str, InterpretResult] = field(default_factory=dict)

@dataclass
class EntitySnapshot:
    constants: dict[str, int] = field(default_factory=lambda: {CONST_ZERO: 0, CONST_ASSERTION_DISABLED : 0}) # cached values
    method_hashes: dict[str, int] = field(default_factory=dict) # hash does not include constants values
    method_constants: dict[str, set[str]] = field(default_factory=dict)


@dataclass
class SnapshotDiff:
    changed_methods: set[str]
    changed_constants: set[str]

    def __init__(self):
        self.changed_methods = set()
        self.changed_constants = set()

# time is stored as nano seconds
@dataclass
class DeltaResult:
    t_prev_codebase: float = None
    prev_codebase: Codebase = None
    t_next_codebase: float = None
    next_codebase: Codebase = None
    t_prev_snapshot: float = None
    prev_snapshot: EntitySnapshot = None
    t_next_snapshot: float = None
    next_snapshot: EntitySnapshot = None
    t_prev_saved_result: float = None
    prev_saved_result: SavedResult = None
    t_next_saved_result: float = None
    next_saved_result: SavedResult = None
    t_new_tests: float = None
    new_tests: set[str] = None
    t_diff: float = None
    diff: SnapshotDiff = None
    
    t_save_and_restore: float = None

    t_run_all_tests: float = None
    t_run_necessary_tests: float = None

    def entire_prev_run(self):
        return sum([
            self.t_prev_codebase,
            self.t_prev_saved_result,
            self.t_prev_snapshot,
            self.t_run_all_tests
        ])
    
    def entire_next_run(self):
        return sum([
            self.t_next_codebase,
            self.t_next_saved_result,
            self.t_next_snapshot,
            self.t_run_necessary_tests
        ])

    def times(self):
        return {
            "t_prev_codebase": self.t_prev_codebase,
            "t_next_codebase": self.t_next_codebase,
            "t_prev_snapshot": self.t_prev_snapshot,
            "t_next_snapshot": self.t_next_snapshot,
            "t_prev_saved_result": self.t_prev_saved_result,
            "t_next_saved_result": self.t_next_saved_result,
            "t_new_tests": self.t_new_tests,
            "t_diff": self.t_diff,
            "t_save_and_restore": self.t_save_and_restore,
            
            "t_run_all_tests": self.t_run_all_tests,
            "t_run_necessary_tests": self.t_run_necessary_tests,
        }

