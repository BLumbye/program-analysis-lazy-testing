from __future__ import annotations
from dataclasses import dataclass, field
from common.binary_expression import BinaryExpr
from common.common import CONST_ZERO, CONST_ASSERTION_DISABLED

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
