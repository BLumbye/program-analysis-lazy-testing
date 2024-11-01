from __future__ import annotations
from dataclasses import dataclass
from enum import Enum

#TODO: rename functions to methods

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

    ADD = "+", #incr can be stored as add
    SUB = "-",
    MUL = "*",
    DIV = "/",
    REM = "%"

class UnaryOp(str, Enum):
    NEG = "-1",
    NOT = "!" # introduced to make it easier to save constraints

class ValueKind(str, Enum):
    CONST = "@CONST",
    IMMED = "@IMMED"

@dataclass
class Value:
    kind: ValueKind
    value: str | int # CONST is str | IMMED is int

@dataclass
class UnaryExpr:
    arg: Expr
    operator: UnaryOp
    cache_id: int # a unique id, so we can cache part of the computation 

@dataclass
class BinaryExpr:
    left: Expr
    right: Expr
    operator: BinaryOp
    cache_id: int # a unique id, so we can cache part of the computation 

Expr = BinaryExpr | UnaryExpr | Value

@dataclass
class Constraint:
    # if it is not too inefficient it would be nice to have a depends on constants here.
    test_name: str
    cache_size: int # the number of unique ids in the constraint
    expr: Expr

# Note: result is written so it is able to be serialized
@dataclass
class InterpretResult:
    test_name: str
    status: str # The same status as JPAMB
    depends_on_constants: list[str]
    depends_on_functions: list[str]
    constraints: list[Constraint]

# The thing stored in JSON
@dataclass
class SavedResult:
    entity_changes_tests: dict[str, list[str]] # 
    tests: dict[str, InterpretResult]
    snapshot: EntitySnapshot

@dataclass
class EntitySnapshot:
    constants: dict[str, int] # cached values
    method_hashes: dict[str, int] # hash does not include constants values

    def __init__(self):
        self.constants = {}
        self.method_hashes = {}

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
    # classname -> list of bytecode for methods
    _fields = dict[str, list[object]]
    # classname -> list of bytecode for test methods
    _tests = dict[str, list[object]]
    # classname -> bytecode for class
    bytecode = dict[str, object]
    def __init__(self, bytecode: dict[str, object]):
        self.bytecode = bytecode
        self._methods = {}
        self._tests = {}
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
        return self._methods[class_name, method_name][0]
    
    def get_tests(self) -> dict[str, object]:
        return self._tests
    
    def get_class_tests(self, class_name) -> list[object]:
        return self._tests[class_name]
    
    def get_fields(self) -> dict[str, list[object]]:
        return self._fields
