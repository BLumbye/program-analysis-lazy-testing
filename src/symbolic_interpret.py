from collections import deque
from typing import override
from interpreter import SimpleInterpreter, Method
from dataclasses import dataclass
from pathlib import Path
import sys
import logging
from typing import Literal, TypeAlias, Optional
from collections import deque
import json


#To override methods
#
#

class ChildMethod(Method):
    symbolic_stack = deque
    linear_constraint_stack = deque

class SymbolicInterpreter(SimpleInterpreter):

    method_stack: deque[ChildMethod]
    @override
    def step_load(self, bc):
        value = self.method_stack[-1].locals[bc["index"]]
        self.method_stack[-1].stack.append(value)
        symbol = self.method_stack[-1].symbolic_stack[0]+len(self.method_stack[-1].symbolic_stack)+1
        self.method_stack[-1].symbolic_stack.append((value,symbol))
        self.method_stack[-1].pc += 1

    @override
    def step_binary(self, bc):
        value2 = self.method_stack[-1].stack.pop()
        value1 = self.method_stack[-1].stack.pop()
        _,expr = self.method_stack[-1].symbolic_stack.pop()
        
        if value1 in self.method_stack[-1].symbolic_stack[-1]:
            _,expr2 = self.method_stack[-1].symbolic_stack.pop()

        match bc["operant"]:
            case "add":
                self.method_stack[-1].stack.append(value1 + value2)
                new_expr = expr+'+'+expr2
                self.method_stack[-1].symbolic_stack.append((value1 + value2,new_expr))
            case "sub":
                self.method_stack[-1].stack.append(value1 - value2)
                new_expr = expr+'-'+expr2
                self.method_stack[-1].symbolic_stack.append((value1 - value2,new_expr))
            case "mul":
                self.method_stack[-1].stack.append(value1 * value2)
                new_expr = expr+'*'+expr2
                self.method_stack[-1].symbolic_stack.append((value1 * value2,new_expr))
            case "div":
                if value2 == 0:
                    self.done = "divide by zero"
                else:
                    if bc["type"] == "int":
                        self.method_stack[-1].stack.append(value1 // value2)
                        new_expr = expr+'//'+expr2
                        self.method_stack[-1].symbolic_stack.append((value1 // value2,new_expr))
                    else:
                        self.method_stack[-1].stack.append(value1 / value2)
                        new_expr = expr+'/'+expr2
                        self.method_stack[-1].symbolic_stack.append((value1 / value2,new_expr))
            case "rem":
                if value2 == 0:
                    self.done = "divide by zero"
                else:
                    self.method_stack[-1].stack.append(value1 % value2)
                    new_expr = expr+'%'+expr2
                    self.method_stack[-1].symbolic_stack.append((value1 % value2,new_expr))
        self.method_stack[-1].pc += 1
    
    @override
    def step_store(self, bc):
        while (len(self.method_stack[-1].locals) <= bc["index"]):
            self.method_stack[-1].locals.append(0)
        self.method_stack[-1].locals[bc["index"]
                                     ] = self.method_stack[-1].stack.pop()
        self.method_stack[-1].symbolic_stack.pop()
        self.method_stack[-1].pc += 1

    @override
    def step_ifz(self, bc):
        value = self.method_stack[-1].stack.pop()
        expr = self.method_stack[-1].symbolic_stack.pop()
        result = False
        match bc["condition"]:
            case "eq":
                result = value == 0
                self.method_stack[-1].linear_constraint_stack.append(expr+'==0')
            case "ne":
                result = value != 0
                self.method_stack[-1].linear_constraint_stack.append(expr+'!=0')
            case "lt":
                result = value < 0
                self.method_stack[-1].linear_constraint_stack.append(expr+'<0')
            case "ge":
                result = value >= 0
                self.method_stack[-1].linear_constraint_stack.append(expr+'>=0')
            case "gt":
                result = value > 0
                self.method_stack[-1].linear_constraint_stack.append(expr+'>0')
            case "le":
                result = value <= 0
                self.method_stack[-1].linear_constraint_stack.append(expr+'<=0')
            case _:
                self.done = f"can't handle {
                    bc['condition']!r} for ifz operations"
        if result:
            self.method_stack[-1].pc = bc["target"]
        else:
            self.method_stack[-1].pc += 1

    @override
    def step_if(self, bc):
        value2 = self.method_stack[-1].stack.pop()
        value1 = self.method_stack[-1].stack.pop()
        _,expr = self.method_stack[-1].symbolic_stack.pop()
        if value1 in self.method_stack[-1].symbolic_stack[-1]:
            _,expr2 = self.method_stack[-1].symbolic_stack.pop()
      
        result = False
        match bc["condition"]:
            case "eq":
                result = value1 == value2
                if not expr2 is None:
                    self.method_stack[-1].linear_constraint_stack.append(expr+'=='+expr2)
                else:
                    self.method_stack[-1].linear_constraint_stack.append(expr+'=='+value1)
            case "ne":
                result = value1 != value2
                if not expr2 is None:
                    self.method_stack[-1].linear_constraint_stack.append(expr+'!='+expr2)
                else:
                    self.method_stack[-1].linear_constraint_stack.append(expr+'!='+value1)
            case "lt":
                result = value1 < value2
                if not expr2 is None:
                    self.method_stack[-1].linear_constraint_stack.append(expr+'<'+expr2)
                else:
                    self.method_stack[-1].linear_constraint_stack.append(expr+'<'+value1)
            case "ge":
                result = value1 >= value2
                if not expr2 is None:
                    self.method_stack[-1].linear_constraint_stack.append(expr+'>='+expr2)
                else:
                    self.method_stack[-1].linear_constraint_stack.append(expr+'>='+value1)
            case "gt":
                result = value1 > value2
                if not expr2 is None:
                    self.method_stack[-1].linear_constraint_stack.append(expr+'>'+expr2)
                else:
                    self.method_stack[-1].linear_constraint_stack.append(expr+'>'+value1)
            case "le":
                result = value1 <= value2
                if not expr2 is None:
                    self.method_stack[-1].linear_constraint_stack.append(expr+'<='+expr2)
                else:
                    self.method_stack[-1].linear_constraint_stack.append(expr+'<='+value1)
            case _:
                self.done = f"can't handle {
                    bc['condition']!r} for if operations"
        if result:
            self.method_stack[-1].pc = bc["target"]
        else:
            self.method_stack[-1].pc += 1
    