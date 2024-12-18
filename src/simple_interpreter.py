from copy import deepcopy
import logging as l
from collections import deque
from dataclasses import dataclass, field
from typing import Optional

from common.common import abs_method_name, CONST_ASSERTION_DISABLED, constant_name
from common.codebase import Codebase
from common.results import InterpretResult
from common.expressions import *

l.basicConfig(level=l.DEBUG, format="%(message)s")

class AssertionError:
    def throw(self):
        return "assertion error"

@dataclass
class Method:
    class_name: str
    name: str
    bytecode: list
    locals: list
    stack: deque
    pc: int = field(default_factory=int)

# Use dedicated variable to disable logging, because if we rely on l.disable(l.DEBUG) we still pay for creating string
should_log = False

def set_should_log(v):
    global should_log
    should_log = v

# Does not have an explicit heap  as we just use the built-in from Python
@dataclass
class SimpleInterpreter:
    codebase: Codebase
    # classname -> fieldname -> value
    fields: dict[str, dict[str, object]]
    method_stack: deque[Method]
    done: Optional[str] = None
    step_count: int = 0
    
    constant_dependencies = set()
    method_dependencies = set()
    _next_cache_ID: int = 0
    _cache_size: int = 0
    _constraints = list()
    
    def __init__(self, codebase: Codebase, method_stack: deque[Method]):
        self.codebase = codebase
        self.method_stack = method_stack
        self.constant_dependencies = set()
        self.method_dependencies = set([abs_method_name(m.class_name, m.name) for m in method_stack])
        self.linear_constraint_stack = []
        self.fields = deepcopy(codebase.get_fields())
        self._constraints = []

    def current_method(self) -> Method: 
        return self.method_stack[-1]

    def debug_step(self, next):
        l.debug(f"STEP {self.step_count}:")
        l.debug(f"  METHOD: {self.current_method().class_name}.{self.current_method().name}")
        l.debug(f"  PC: {self.current_method().pc} {next}")
        l.debug(f"  LOCALS: {self.current_method().locals}")
        l.debug(f"  STACK: {self.current_method().stack}")

    def step(self):
        self.step_count += 1
        
        if self.current_method().pc >= len(self.current_method().bytecode):
            if len(self.method_stack) > 1:
                self.method_stack.pop()
            else:
                self.done = "ok"
                return
        next = self.current_method().bytecode[self.current_method().pc]
        if should_log:
            self.debug_step(next)
        
        if fn := getattr(self, "step_" + next["opr"], None):
            self.current_method().pc += 1
            fn(next)
        else:
            raise Exception(f"can't handle {next['opr']!r}")
    
    def interpret(self, limit=100000) -> InterpretResult:
        for _ in range(limit):
            self.step()
            if self.done:
                break
        else:
            self.done = "*"

        if should_log:
            l.debug(f"DONE {self.done}")
            l.debug(f"  LOCALS: {self.current_method().locals}")
            l.debug(f"  STACK: {self.current_method().stack}")

        return InterpretResult(
            self.method_stack[0].name, 
            self.done, 
            list(self.method_dependencies), 
            list(self.constant_dependencies), 
            self._constraints, 
            self._cache_size
        )
    
    def step_get(self, bc):
        # Getting a static field from another class inside <clinit> is not allowed
        if self.current_method().name == "<clinit>" and bc["field"]["class"] != self.current_method().class_name:
            self.done = "field initialization must not reference other classes"
            return
        if not bc["static"]:
            self.done = "non-static fields not implemented"
            return
        
        self.current_method().stack.append(self.fields[bc["field"]["class"]][bc["field"]["name"]])
        self.constant_dependencies.add(constant_name(bc["field"]["name"], bc["field"]["class"]))

    def step_put(self, bc):
        if not bc["static"]:
            self.done = "non-static fields not implemented"
            return
        self.fields[bc["field"]["class"]][bc["field"]["name"]] = self.current_method().stack.pop()

    # Missing 'is' and 'notis' conditions (probably meant for isnull and isnonnull, but unclear)
    def __if(self, bc, inst_name, value1, value2):
        bc_condition = bc["condition"]

        if (cond := IF_CONDITION_HANDLERS.get(bc_condition)) is not None:
            result, _ = cond(value1, value2)
            if result:
                self.current_method().pc = bc["target"]
        else:
            self.done = f"can't handle {bc_condition!r} for {inst_name} operations"

    def step_if(self, bc):
        value2 = self.current_method().stack.pop()
        value1 = self.current_method().stack.pop()
        self.__if(bc, "if", value1, value2)

    def step_ifz(self, bc):
        value = self.current_method().stack.pop()
        self.__if(bc, "ifz", value, 0)

    # Properly interpreting this requires more knowledge of the class which we don't have.
    def step_new(self, bc):
        _class = bc["class"]
        match _class:
            case "java/lang/AssertionError":
                self.current_method().stack.append(AssertionError())
            case _:
                self.done = f"can't handle {_class!r} for new operations"

    def step_dup(self, _):
        self.current_method().stack.append(self.current_method().stack[-1])

    # Only handles static methods properly
    def step_invoke(self, bc):
        access = bc["access"]
        if bc["method"]["ref"]["name"] == "java/lang/Class" and bc["method"]["name"] == "desiredAssertionStatus":
            # We always want assertions to be enabled
            self.current_method().stack.pop()
            self.current_method().stack.append(1)
        elif access == "special":
            object_ref = self.current_method().stack.pop()
        elif access == "static":
            next_method_class = bc["method"]["ref"]["name"]
            next_method_name = bc["method"]["name"]
            new_method = self.codebase.get_method(next_method_class, next_method_name, [])

            locals = deque()
            for arg in bc["method"]["args"]:
                locals.append(self.current_method().stack.pop())

            method = Method(next_method_class, next_method_name, new_method["code"]["bytecode"], locals, deque(), 0)
            self.method_stack.append(method)
            
            self.method_dependencies.add(abs_method_name(next_method_class, next_method_name))
        else:
            self.done = f"can't handle {access!r} for invoke operations"

    def step_throw(self, _):
        message = self.current_method().stack[-1].throw()
        self.done = message

    def step_load(self, bc):
        value = self.current_method().locals[bc["index"]]
        self.current_method().stack.append(value)

    def step_binary(self, bc):
        value2 = self.current_method().stack.pop()
        value1 = self.current_method().stack.pop()
        bc_operant = bc["operant"]

        if value2 == 0 and bc_operant in ["div", "rem"]:
            self.done = "divide by zero"
            return

        if (operant := BINARY_OPERATION_HANDLERS.get(bc_operant)) is not None:
            result, _ = operant(value1, value2)
            self.current_method().stack.append(result)
        else:
            self.done = f"can't handle {bc_operant!r} for binary operations"

    def step_negate(self, _):
        value = self.current_method().stack.pop()
        self.current_method().stack.append(-value)

    def step_goto(self, bc):
        self.current_method().pc = bc["target"]

    def step_store(self, bc):
        while (len(self.current_method().locals) <= bc["index"]):
            self.current_method().locals.append(0)

        value = self.current_method().stack.pop()
        self.current_method().locals[bc["index"]] = value

    # Not properly implemented, casting in Loops is only from int to short and does not matter in this case
    def step_cast(self, bc):
        cast_type = bc['to']
        value = self.current_method().stack.pop()
        new_value = None

        match cast_type:
            case 'short':
                new_value = self.int_to_short(value)
            case 'byte':
                new_value = self.int_to_byte(value)
            case 'char':
                new_value = chr(value)
            case _:
                self.done = f"can't handle {cast_type!r} when casting"
        
        self.current_method().stack.append(new_value)

    @staticmethod
    def int_to_short(value):
        # Apply a mask to simulate 16-bit signed integer range (-32768 to 32767)
        short_value = (value & 0xFFFF)
        if short_value >= 0x8000:  # If the value exceeds 32767
            short_value -= 0x10000  # Convert to negative (two's complement)
        return short_value

    @staticmethod
    def int_to_byte(value):
        # Apply a mask to simulate 8-bit signed integer range (-128 to 127)
        byte_value = (value & 0xFF)
        if byte_value >= 0x80:  # If the value exceeds 127
            byte_value -= 0x100  # Convert to negative (two's complement)
        return byte_value

    # Only handles 1-dimensional integer arrays, not multi-dimensional
    def step_newarray(self, bc):
        if bc["dim"] != 1:
            self.done = f"can't handle multi-dimensional arrays"
        elif bc["type"] != "int":
            self.done = f"can't handle {bc['type']!r} for newarray operations"
        else:
            size = self.current_method().stack.pop()
            self.current_method().stack.append([0] * size)

    def _check_array(self, array: Optional[list], index: Optional[int]) -> bool:
        if array is None:
            self.done = "null pointer"
            return False
        
        if index is not None and index >= len(array):
            self.done = "out of bounds"
            return False

        return True

    def step_array_store(self, _):
        value = self.current_method().stack.pop()
        index = self.current_method().stack.pop()
        array = self.current_method().stack.pop()
        if not self._check_array(array, index):
            return
        array[index] = value

    def step_array_load(self, _):
        index = self.current_method().stack.pop()
        array = self.current_method().stack.pop()
        if not self._check_array(array, index):
            return
        self.current_method().stack.append(array[index])

    def step_arraylength(self, _):
        array = self.current_method().stack.pop()
        if not self._check_array(array, None):
            return
        self.current_method().stack.append(len(array))

    def step_incr(self, bc):
        amount_expr = constant_name(self.current_method().pc - 1, self.current_method().class_name, self.current_method().name)
        self.constant_dependencies.add(amount_expr)
        
        self.current_method().locals[bc["index"]] += bc["amount"]

    def step_push(self, bc):
        expr = constant_name(self.current_method().pc - 1, self.current_method().class_name, self.current_method().name)
        self.constant_dependencies.add(expr)
        self.current_method().stack.append(bc["value"]["value"] if bc["value"] else None)

    def step_pop(self, bc):
        for _ in range(bc["words"]):
            self.current_method().stack.pop()

    def step_return(self, bc):
        if len(self.method_stack) > 1:
            # Method return
            if bc["type"] is not None:
                self.method_stack[-2].stack.append(
                    self.current_method().stack.pop()
                )
            self.method_stack.pop()
        else:
            # Program return
            self.done = "ok"
