from dataclasses import dataclass
from typing import List, Dict
from __future__ import annotations


# if you load an anonymous variable name using push, then use the "offset" as the variable name
# if you load a variable from a class the function name is None
def constant_name(variable_name, class_name, function_name = None):
    parts = [class_name, function_name, variable_name]
    parts = filter((lambda x: x != None), parts)
    parts = map(str, parts)
    return ":".join(parts)


def function_name(class_name, function_name):
    parts = [class_name, function_name]
    parts = filter((lambda x: x != None), parts)
    parts = map(str, parts)
    return ":".join(parts)





@dataclass
class Expr:
    left: Expr | str # str means it is a constant
    right: Expr | str # str means it is a constant
    # We are not using enum because of JSON(might be wrong, haven't looked into it)
    operation: str # oneof {"+", "-", "*", "/", "%"}
    cache_id: str # a unique id, so we can cache part of the computation

@dataclass
class Constraint:
    # if it is not too inefficient it would be nice to have a depends on constants here.
    test_name: str
    left: Expr
    right: Expr
    comparator: str # oneof {"<", "<=", "==", "!=", ">", ">="}

# Note: result is written so it is able to be serialized
@dataclass
class InterpretResult:
    test_name: str
    status: str # The same status as JPAMB
    depends_on_constants: List[str]
    depends_on_functions: List[str]
    constraints: List[Constraint]



# very unfinished
@dataclass
class GenericInterpreter:
    def __init__(json_classes: Dict[str, object], initial_function: str):
        # Question: Do we ever want to support calling functions across files?
        pass
    def interpret(self, limit:int) -> InterpretResult:
        pass



# 

