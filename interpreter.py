#!/usr/bin/env python3
""" The skeleton for writing an interpreter given the bytecode.
"""

from dataclasses import dataclass
from pathlib import Path
import sys
import logging
from typing import Literal, TypeAlias, Optional
from collections import deque
import json
import jpamb_utils as utils

l = logging
l.basicConfig(level=logging.DEBUG, format="%(message)s")


class AssertionError:
    def throw(self):
        return "assertion error"


@dataclass
class Method:
    bytecode: list
    locals: list
    stack: deque
    pc: int


# Does not have an explicit heap or method stack as we just use the built-in from Python
@dataclass
class SimpleInterpreter:
    # heap: deque
    method_stack: deque[Method]
    done: Optional[str] = None

    def interpret(self, limit=1000):
        for i in range(limit):
            if self.method_stack[-1].pc >= len(self.method_stack[-1].bytecode):
                if len(self.method_stack) > 1:
                    self.method_stack.pop()
                else:
                    self.done = "ok"
                    break

            next = self.method_stack[-1].bytecode[self.method_stack[-1].pc]
            l.debug(f"STEP {i}:")
            l.debug(f"  PC: {self.method_stack[-1].pc} {next}")
            l.debug(f"  LOCALS: {self.method_stack[-1].locals}")
            l.debug(f"  STACK: {self.method_stack[-1].stack}")

            if fn := getattr(self, "step_" + next["opr"], None):
                fn(next)
            else:
                return (f"can't handle {next['opr']!r}", None)

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
                self.done = f"can't handle {
                    bc['condition']!r} for if operations"
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
                self.done = f"can't handle {
                    bc['condition']!r} for ifz operations"
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
        TYPE_LOOKUP: dict[utils.JvmType, str] = {
            "boolean": "Z",
            "int": "I",
        }

        if bc["access"] == "special":
            object_ref = self.method_stack[-1].stack.pop()
            self.method_stack[-1].pc += 1
        elif bc["access"] == "static":
            # Translate the information to the format used by MethodId - only handles up to a single argument and does not handle array arguments
            arg_count = len(bc["method"]["args"])
            arg_type = TYPE_LOOKUP[bc["method"]
                                   ["args"][0]] if arg_count > 0 else ""
            return_type = "V"
            if isinstance(bc["method"]["returns"], dict) and bc["method"]["returns"]["kind"] == "array":
                return_type = f"[{
                    TYPE_LOOKUP[bc["method"]["returns"]["type"]]}"
            elif bc["method"]["returns"] != None:
                return_type = TYPE_LOOKUP[bc["method"]["returns"]]
            method_name = f"{bc["method"]["ref"]["name"].replace(
                "/", ".")}.{bc["method"]["name"]}:({arg_type}){return_type}"
            method_id = utils.MethodId.parse(
                method_name)
            bytecode = method_id.load()["code"]["bytecode"]
            locals = deque()
            for i in range(arg_count):
                locals.append(self.method_stack[-1].stack.pop())
            method = Method(bytecode, locals, [], 0)
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
        new_value:None
        if cast_type =='short':
            new_value = self.int_to_short(value)
        if cast_type == 'byte':
            new_value = self.int_to_byte(value)
        if cast_type == 'char':
            new_value = chr(value)
        self.stack.append(new_value)
        self.pc+=1
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


if __name__ == "__main__":
    methodid = utils.MethodId.parse(sys.argv[1])
    inputs = utils.InputParser.parse(sys.argv[2])
    method = methodid.load()
    # Convert all inputs to integers
    inputs = [[l.tolocal() for l in i.value] if isinstance(
        i, utils.IntListValue) or isinstance(i, utils.CharListValue) else i.tolocal() for i in inputs]
    interpreter = SimpleInterpreter(
        # heap=deque(),
        method_stack=deque(
            [Method(method["code"]["bytecode"], inputs, [], 0)])
    )
    print(interpreter.interpret())
