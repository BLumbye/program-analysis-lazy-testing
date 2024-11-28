from __future__ import annotations
import json 
import hashlib

from common.common import *
from common.codebase import *
from common.results import *

def copy_dict_except(dict, exceptions):
    return { k:v for k, v in dict.items() if k not in exceptions }
    
def method_snapshot(snapshot: EntitySnapshot, class_name: str, curr_method: object, codebase: Codebase, visited: set[str]):
    hash_str = ""
    method_name = curr_method["name"]
    method_bytecode = curr_method["code"]["bytecode"]
    method_constants = set()
    
    for i, inst in enumerate(method_bytecode):
        match inst["opr"]:
            case "push":
                const_name = constant_name(i, class_name, method_name)
                snapshot.constants[const_name] = int(inst["value"]["value"]) if inst["value"] else None
                method_constants.add(const_name)
                hash_str += "push"
                
            case "incr":
                const_name = constant_name(i, class_name, method_name)
                snapshot.constants[const_name] = int(inst["amount"])
                method_constants.add(const_name)
                hash_str += "incr"
                
            case "get":
                const_name = constant_name(inst["field"]["name"], class_name)
                method_constants.add(const_name)
                hash_str += "get"
                
            case "invoke":
                if inst["access"] == "static":
                    next_class_name = inst["method"]["ref"]["name"]
                    next_name = inst["method"]["name"]
                    next_method = codebase.get_method(next_class_name, next_name, [])

                    if next_name not in visited:
                        visited.add(next_name)
                        method_snapshot(snapshot, class_name, next_method, codebase, visited)
                        
                # The offset might change for unknown reasons, therefore remove it
                hash_str += json.dumps(copy_dict_except(inst, ["offset"])) # TODO: optimize
            case _:
                # The offset might change for unknown reasons, therefore remove it
                hash_str += json.dumps(copy_dict_except(inst, ["offset"])) # TODO: optimize

    method_name = abs_method_name(class_name, method_name)
    # md5 is used as a cheap hash function
    snapshot.method_hashes[method_name] = hashlib.md5(hash_str.encode()).hexdigest()
    snapshot.method_constants[method_name] = method_constants

def field_snapshot(snapshot: EntitySnapshot, class_name: str, field_name: str, value: object):
    name = constant_name(field_name, class_name)
    snapshot.constants[name] = value

# Assumes all tests are annotated with @Test
def codebase_snapshot(codebase: Codebase) -> EntitySnapshot:
    visited = set()
    snapshot = EntitySnapshot()

    for class_name, fields in codebase.get_fields().items():
        for field_name, field_value in fields.items():
            field_snapshot(snapshot, class_name, field_name, field_value)

    for class_name, tests in codebase.get_tests().items():
        for test in tests:
            method_snapshot(snapshot, class_name, test, codebase, visited)
                
    return snapshot

def diff_snapshots(prev: EntitySnapshot, next: EntitySnapshot) -> SnapshotDiff:
    diff = SnapshotDiff()

    for name, value in prev.method_hashes.items():
        if (name not in next.method_hashes.keys() 
            or next.method_hashes[name] != value):

            diff.changed_methods.add(name)

    for name, value in prev.constants.items():
        if (name not in next.constants.keys() 
            or next.constants[name] != value):
            
            diff.changed_constants.add(name)

    return diff
