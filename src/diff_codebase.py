from __future__ import annotations
from dataclasses import dataclass
import json 
import hashlib

from common import *

@dataclass
class SnapshotDiff:
    changed_methods: set[str]
    changed_constants: set[str]

    def __init__(self):
        self.changed_methods = set()
        self.changed_constants = set()

def method_snapshot(snapshot: EntitySnapshot, class_name: str, curr_method: object, codebase: CodeBase, visited: set[str]):
    hash_str = ""
    method_name = curr_method["name"]
    method_bytecode = curr_method["code"]["bytecode"]
    
    for inst in method_bytecode:
        match inst["opr"]:
            case "push":
                const_name = constant_name(str(inst["offset"]), class_name, method_name)
                snapshot.constants[const_name] = int(inst["value"]["value"]) #TODO: cast value to int
                
            case "invoke":
                if inst["access"] == "static":
                    next_class_name = inst["method"]["ref"]["name"]
                    next_name = inst["method"]["name"]
                    next_method = codebase.get_method(next_class_name, method_name, [])

                    if next_name not in visited:
                        visited.add(next_name)
                        method_snapshot(snapshot, class_name, next_method, codebase, visited)
                hash_str += json.dumps(inst) # TODO: optimize
                
            case _:
                hash_str += json.dumps(inst) # TODO: optimize

    method_name = function_name(class_name, method_name)
    # md5 is used as a cheap hash function
    snapshot.method_hashes[method_name] = hashlib.md5(hash_str.encode()).hexdigest()

def field_snapshot(snapshot: EntitySnapshot, class_name: str, field: object):
    # ignore fields with synthetic in access (compiler-created fields)
    if "synthetic" not in field["access"]:
        field_name = constant_name(field["name"], class_name)
        snapshot.constants[field_name] = int(field["value"]["value"]) #TODO: cast value to int

# Assumes all tests are annotated with @Test
def codebase_snapshot(codebase: CodeBase) -> EntitySnapshot:
    visited = set()
    snapshot = EntitySnapshot()

    for class_name, field in codebase.get_fields().items():
        field_snapshot(snapshot, class_name, field)

    for class_name, test in codebase.get_tests().items():
        method_snapshot(snapshot, class_name, test, codebase, visited)
                
    return snapshot

def diff_snapshots(prev: EntitySnapshot, next: EntitySnapshot) -> SnapshotDiff:
    diff = SnapshotDiff()

    for name, value in prev.method_hashes.items():
        if next.method_hashes[name] != value: 
            diff.changed_methods.add(name)

    for name, value in prev.constants.items():
        if next.constants[name] != value: 
            diff.changed_constants.add(name)

    return diff
