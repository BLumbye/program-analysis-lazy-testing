from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
import os
import json

# TODO: rename functions to methods

# if you load an anonymous variable name using push, then use the "offset" as the variable name
# if you load a variable from a class the function name is None
def constant_name(variable_name, class_name, function_name = None):
    parts = [class_name, function_name, variable_name]
    parts = filter((lambda x: x != None), parts)
    parts = map(str, parts)
    return ":".join(parts)

# TODO: rename to method_name
def function_name(class_name, function_name):
    parts = [class_name, function_name]
    parts = filter((lambda x: x != None), parts)
    parts = map(str, parts)
    return ":".join(parts)

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

# Translation Note (Unary):
# Incr can be stored as add/sub
# NEG (0 - x)
# Not once (x == false)

@dataclass
class BinaryExpr:
    left: Expr
    operator: BinaryOp
    right: Expr
    cache_id: int # a unique id [0-n], so we can cache part of the computation 

Expr = BinaryExpr | str # str is a constant_name

# @dataclass
# class Constraint:
#     # if it is not too inefficient it would be nice to have a depends on constants here.
#     test_name: str
#     cache_size: int # the number of unique ids in the constraint
#     expr: Expr

# Note: result is written so it is able to be serialized
@dataclass
class InterpretResult:
    test_name: str
    status: str # The same status as JPAMB
    depends_on_constants: list[str]
    depends_on_functions: list[str]
    constraints: list[BinaryExpr]
    cache_size: int  # the number of unique cache ids

# The thing stored in JSON
@dataclass
class SavedResult:
    snapshot: EntitySnapshot
    entity_changes_tests: dict[str, list[str]] = field(default_factory=dict)
    tests: dict[str, InterpretResult] = field(default_factory=dict)

    def __init__(self, snapshot: EntitySnapshot):
        self.entity_changes_tests = {}
        self.tests = {}
        self.snapshot = snapshot

@dataclass
class EntitySnapshot:
    constants: dict[str, int] = field(default_factory=dict) # cached values
    method_hashes: dict[str, int] = field(default_factory=dict) # hash does not include constants values

# very unfinished
@dataclass
class GenericInterpreter:
    def __init__(json_classes: dict[str, object], initial_function: str):
        # Question: Do we ever want to support calling functions across files?
        pass
    def interpret(self, limit:int) -> InterpretResult:
        pass

# Can both be a next and previous codebase
@dataclass
class CodeBase:
    # classname -> methodname -> list of methods (they might have different arguments)
    _methods = dict[str, dict[str, list[object]]]
    # classname -> list of bytecode for fields
    _fields = dict[str, list[object]]
    # classname -> list of bytecode for test methods
    _tests = dict[str, list[object]]
    # classname -> bytecode for class
    bytecode = dict[str, object]

    def __init__(self, bytecode: dict[str, object]):
        self.bytecode = bytecode
        self._methods = {}
        self._tests = {}
        self._fields = {}
        for class_name, _class in bytecode.items():
            if class_name not in self._methods:
                self._methods[class_name] = {}
            if class_name not in self._tests:
                self._tests[class_name] = []

            self._fields[class_name] = _class["fields"]

            for method in _class["methods"]:
                method_name = method["name"]
                is_test = any(a["type"] == "utils/Test" for a in method["annotations"])
                if is_test:
                    self._tests[class_name].append(method)
                if method_name not in self._methods[class_name]:
                    self._methods[class_name][method_name] = []
                    
                self._methods[class_name][method_name].append(method)            

    def get_classes(self) -> dict[str, object]:
        return self.bytecode
    
    def get_class_names(self) -> list[str]:
        return self.bytecode.keys()

    def get_class(self, class_name) -> object:
        return self.bytecode[class_name]

    def get_class_methods(self, class_name) -> dict[str, list[object]]:
        return self._methods[class_name]

    def get_method(self, class_name, method_name, arguments) -> object:
        # TODO: handle argument overloading
        return self._methods[class_name][method_name][0]
    
    def get_tests(self) -> dict[str, object]:
        return self._tests
    
    def get_class_tests(self, class_name) -> list[object]:
        return self._tests[class_name]

    def all_test_names(self) -> list[str]:
        test_names = []
        for c, tests in self.get_tests().items():
            for t in tests:
                test_names.append(function_name(c, t["name"]))
        return test_names
         
    
    def get_fields(self) -> dict[str, list[object]]:
        return self._fields

def all_file_paths(dir: str):
    paths = []
    for root, _, filenames in os.walk(dir):
        for name in filenames:
            paths.append((os.path.splitext(name)[0], os.path.join(root, name)))
    
    return paths

def code_base_path(codebase: str):
    return os.path.join(os.path.dirname(__file__), "..", "codebases", codebase)

def load_decompiled(codebase_dir: str, is_next: bool) -> CodeBase:
    bytecode = dict()
    dir = "next" if is_next else "previous"
    for name, file_path in all_file_paths(os.path.join(codebase_dir, dir, "decompiled")):
        with open(file_path, 'r') as file:
            bytecode[name] = json.load(file)

    return CodeBase(bytecode)

def load_codebase(codebase: str, is_next: bool) -> CodeBase:
    return load_decompiled(code_base_path(codebase), is_next)
