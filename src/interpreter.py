#!/usr/bin/env python3
""" The skeleton for writing an interpreter given the bytecode.
"""

import logging
from collections import deque
from dataclasses import dataclass
from typing import Optional

from common import CodeBase

l = logging
l.basicConfig(level=logging.DEBUG, format="%(message)s")


class AssertionError:
    def throw(self):
        return "assertion error"


@dataclass
class Method:
    name: str
    bytecode: list
    locals: list
    stack: deque
    pc: int


# Does not have an explicit heap  as we just use the built-in from Python
@dataclass
class SimpleInterpreter:
    codebase: CodeBase
    method_stack: deque[Method]
    done: Optional[str] = None
    step_count: int = 0

    def step(self):
        if self.method_stack[-1].pc >= len(self.method_stack[-1].bytecode):
            if len(self.method_stack) > 1:
                self.method_stack.pop()
            else:
                self.done = "ok"
                self.step_count += 1
                return

        next = self.method_stack[-1].bytecode[self.method_stack[-1].pc]
        l.debug(f"STEP {self.step_count}:")
        l.debug(f"  PC: {self.method_stack[-1].pc} {next}")
        l.debug(f"  LOCALS: {self.method_stack[-1].locals}")
        l.debug(f"  STACK: {self.method_stack[-1].stack}")

        if fn := getattr(self, "step_" + next["opr"], None):
            fn(next)
        else:
            self.step_count += 1
            raise Exception(f"can't handle {next['opr']!r}")

        self.step_count += 1

    def interpret(self, limit=1000):
        for i in range(limit):
            self.step()
            if self.done:
                break
        else:
            self.done = "*"

        l.debug(f"DONE {self.done}")
        l.debug(f"  LOCALS: {self.method_stack[-1].locals}")
        l.debug(f"  STACK: {self.method_stack[-1].stack}")

        return self.done

    # Using recommended hack of just setting false when getting '$assertionsDisabled'.
    # The rest of the operation is not used, so not implemented.
    def step_get(self, bc):
        if bc["field"]["name"] == "$assertionsDisabled":
            self.method_stack[-1].stack.append(0)
            self.method_stack[-1].pc += 1
        else:
            self.done = f"can't handle get operations"

    # Missing 'is' and 'notis' conditions (probably meant for isnull and isnonnull, but unclear)
    def step_if(self, bc):
        value2 = self.method_stack[-1].stack.pop()
        value1 = self.method_stack[-1].stack.pop()
        result = False
        match bc["condition"]:
            case "eq":
                result = value1 == value2
            case "ne":
                result = value1 != value2
            case "lt":
                result = value1 < value2
            case "ge":
                result = value1 >= value2
            case "gt":
                result = value1 > value2
            case "le":
                result = value1 <= value2
            case _:
                self.done = f"can't handle {bc['condition']} for if operations"
        if result:
            self.method_stack[-1].pc = bc["target"]
        else:
            self.method_stack[-1].pc += 1

    # As above, missing 'is' and 'notis'
    def step_ifz(self, bc):
        value = self.method_stack[-1].stack.pop()
        result = False
        match bc["condition"]:
            case "eq":
                result = value == 0
            case "ne":
                result = value != 0
            case "lt":
                result = value < 0
            case "ge":
                result = value >= 0
            case "gt":
                result = value > 0
            case "le":
                result = value <= 0
            case _:
                self.done = f"can't handle {bc['condition']} for ifz operations"
        if result:
            self.method_stack[-1].pc = bc["target"]
        else:
            self.method_stack[-1].pc += 1

    # Properly interpreting this requires more knowledge of the class which we don't have.
    def step_new(self, bc):
        match bc["class"]:
            case "java/lang/AssertionError":
                self.method_stack[-1].stack.append(AssertionError())
            case _:
                self.done = f"can't handle {bc['class']!r} for new operations"
        self.method_stack[-1].pc += 1

    def step_dup(self, bc):
        self.method_stack[-1].stack.append(self.method_stack[-1].stack[-1])
        self.method_stack[-1].pc += 1

    # Only handles static methods properly
    def step_invoke(self, bc):
        if bc["access"] == "special":
            object_ref = self.method_stack[-1].stack.pop()
            self.method_stack[-1].pc += 1
        elif bc["access"] == "static":
            new_method = self.codebase.get_method(bc["method"]["ref"]["name"], bc["method"]["name"], [])
            locals = deque()
            for arg in bc["method"]["args"]:
                locals.append(self.method_stack[-1].stack.pop())
            method = Method(bc["method"]["name"], new_method["code"]["bytecode"], locals, [], 0)
            self.method_stack.append(method)
            self.method_stack[-2].pc += 1
        else:
            self.done = f"can't handle {bc['access']!r} for invoke operations"

    def step_throw(self, bc):
        message = self.method_stack[-1].stack[-1].throw()
        self.done = message

    def step_load(self, bc):
        value = self.method_stack[-1].locals[bc["index"]]
        self.method_stack[-1].stack.append(value)
        self.method_stack[-1].pc += 1

    def step_binary(self, bc):
        value2 = self.method_stack[-1].stack.pop()
        value1 = self.method_stack[-1].stack.pop()
        match bc["operant"]:
            case "add":
                self.method_stack[-1].stack.append(value1 + value2)
            case "sub":
                self.method_stack[-1].stack.append(value1 - value2)
            case "mul":
                self.method_stack[-1].stack.append(value1 * value2)
            case "div":
                if value2 == 0:
                    self.done = "divide by zero"
                else:
                    if bc["type"] == "int":
                        self.method_stack[-1].stack.append(value1 // value2)
                    else:
                        self.method_stack[-1].stack.append(value1 / value2)
            case "rem":
                if value2 == 0:
                    self.done = "divide by zero"
                else:
                    self.method_stack[-1].stack.append(value1 % value2)
        self.method_stack[-1].pc += 1

    def step_goto(self, bc):
        self.method_stack[-1].pc = bc["target"]

    def step_store(self, bc):
        while (len(self.method_stack[-1].locals) <= bc["index"]):
            self.method_stack[-1].locals.append(0)
        self.method_stack[-1].locals[bc["index"]
                                     ] = self.method_stack[-1].stack.pop()
        self.method_stack[-1].pc += 1

    # Not properly implemented, casting in Loops is only from int to short and does not matter in this case
    def step_cast(self, bc):
        cast_type = bc['to']
        value = self.stack.pop()
        new_value: None
        if cast_type == 'short':
            new_value = self.int_to_short(value)
        if cast_type == 'byte':
            new_value = self.int_to_byte(value)
        if cast_type == 'char':
            new_value = chr(value)
        self.stack.append(new_value)
        self.pc += 1

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
            size = self.method_stack[-1].stack.pop()
            self.method_stack[-1].stack.append([0] * size)
        self.method_stack[-1].pc += 1

    def step_array_store(self, bc):
        value = self.method_stack[-1].stack.pop()
        index = self.method_stack[-1].stack.pop()
        array = self.method_stack[-1].stack.pop()
        if array == None:
            self.done = "null pointer"
            return
        if index >= len(array):
            self.done = "out of bounds"
            return
        array[index] = value
        self.method_stack[-1].pc += 1

    def step_array_load(self, bc):
        index = self.method_stack[-1].stack.pop()
        array = self.method_stack[-1].stack.pop()
        if array == None:
            self.done = "null pointer"
            return
        if index >= len(array):
            self.done = "out of bounds"
            return
        self.method_stack[-1].stack.append(array[index])
        self.method_stack[-1].pc += 1

    def step_arraylength(self, bc):
        array = self.method_stack[-1].stack.pop()
        if array == None:
            self.done = "null pointer"
            return
        self.method_stack[-1].stack.append(len(array))
        self.method_stack[-1].pc += 1

    def step_incr(self, bc):
        self.method_stack[-1].locals[bc["index"]] += bc["amount"]
        self.method_stack[-1].pc += 1

    def step_push(self, bc):
        if bc["value"] == None:
            self.method_stack[-1].stack.append(None)
        else:
            self.method_stack[-1].stack.append(bc["value"]["value"])
        self.method_stack[-1].pc += 1

    def step_pop(self, bc):
        for i in range(bc["words"]):
            self.method_stack[-1].stack.pop()
        self.method_stack[-1].pc += 1

    def step_return(self, bc):
        if len(self.method_stack) > 1:
            # Method return
            if bc["type"] is not None:
                self.method_stack[-2].stack.append(
                    self.method_stack[-1].stack.pop())
            self.method_stack.pop()
        else:
            # Program return
            self.done = "ok"
