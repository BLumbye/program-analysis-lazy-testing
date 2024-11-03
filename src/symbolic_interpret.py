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
import jpamb_utils as utils

l = logging
l.basicConfig(level=logging.DEBUG, format="%(message)s")

#To override methods
#
#

class ChildMethod(Method):
    symbolic_stack = deque()
    linear_constraint_stack = deque()

class SymbolicInterpreter(SimpleInterpreter):

    method_stack: deque[ChildMethod]

    @override
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
            l.debug(f"  SYMBOLIC STACK: {self.method_stack[-1].symbolic_stack}")
            l.debug(f"  LINEAR CONSTRAINT: {self.method_stack[-1].linear_constraint_stack}")

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
    @override
    def step_load(self, bc):
        value = self.method_stack[-1].locals[bc["index"]]
        self.method_stack[-1].stack.append(value)
        if len(self.method_stack[-1].symbolic_stack) > 0:
            _,expr = self.method_stack[-1].symbolic_stack[0]
            symbol = expr+str(len(self.method_stack[-1].symbolic_stack)+1)
        else:
            symbol = 'x'
        self.method_stack[-1].symbolic_stack.append((value,symbol))
        self.method_stack[-1].pc += 1

    @override
    def step_binary(self, bc):
        value2 = self.method_stack[-1].stack.pop()
        value1 = self.method_stack[-1].stack.pop()
        
        if len(self.method_stack[-1].symbolic_stack)>0:
            _,expr2 = self.method_stack[-1].symbolic_stack.pop()
            expr = None
            if value1 in self.method_stack[-1].symbolic_stack:
                _,expr = self.method_stack[-1].symbolic_stack.pop()

        match bc["operant"]:
            case "add":
                self.method_stack[-1].stack.append(value1 + value2)
                
                if not expr is None:
                            new_expr = expr+'+'+expr2
                else:
                            new_expr = str(value1)+'+'+ expr2
                self.method_stack[-1].symbolic_stack.append((value1 + value2,new_expr))
            case "sub":
                self.method_stack[-1].stack.append(value1 - value2)
                
                if not expr is None:
                            new_expr = expr+'-'+expr2
                else:
                            new_expr =str(value1)+'-'+ expr2
                self.method_stack[-1].symbolic_stack.append((value1 - value2,new_expr))
            case "mul":
                self.method_stack[-1].stack.append(value1 * value2)
                if not expr is None:
                        new_expr = expr+'*'+expr2
                else:
                        new_expr =str(value1) +'*'+expr2
             
                self.method_stack[-1].symbolic_stack.append((value1 * value2,new_expr))
            case "div":
                if value2 == 0:
                    self.done = "divide by zero"
                else:
                    if bc["type"] == "int":
                        self.method_stack[-1].stack.append(value1 // value2)
                        if not expr is None:
                            new_expr = expr+'//'+expr2
                        else:
                            new_expr =str(value1) +'//'+expr2
                        self.method_stack[-1].symbolic_stack.append((value1 // value2,new_expr))
                    else:
                        self.method_stack[-1].stack.append(value1 / value2)
                        if not expr is None:
                            new_expr = expr+'/'+expr2
                        else:
                            new_expr =str(value1) +'/'+expr2
                    
                        self.method_stack[-1].symbolic_stack.append((value1 / value2,new_expr))
            case "rem":
                if value2 == 0:
                    self.done = "divide by zero"
                else:
                    self.method_stack[-1].stack.append(value1 % value2)
                    
                    if not expr is None:
                            new_expr = expr+'%'+expr2
                    else:
                            new_expr =str(value1)+'%'+ expr2
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
        if len(self.method_stack[-1].symbolic_stack):
            _,expr = self.method_stack[-1].symbolic_stack.pop()
            dont = True
        else:
            dont = False
        
        result = False
        match bc["condition"]:
            case "eq":
                result = value == 0
                if dont: self.method_stack[-1].linear_constraint_stack.append(expr+'==0')
            case "ne":
                result = value != 0
                if dont: self.method_stack[-1].linear_constraint_stack.append(expr+'!=0')
            case "lt":
                result = value < 0
                if dont: self.method_stack[-1].linear_constraint_stack.append(expr+'<0')
            case "ge":
                result = value >= 0
                if dont: self.method_stack[-1].linear_constraint_stack.append(expr+'>=0')
            case "gt":
                result = value > 0
                if dont: self.method_stack[-1].linear_constraint_stack.append(expr+'>0')
            case "le":
                result = value <= 0
                if dont: self.method_stack[-1].linear_constraint_stack.append(expr+'<=0')
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
        if len(self.method_stack[-1].symbolic_stack) > 0:
            _,expr2 = self.method_stack[-1].symbolic_stack.pop()
            if value1 in self.method_stack[-1].symbolic_stack[-1]:
                _,expr = self.method_stack[-1].symbolic_stack.pop()
        
        result = False
        match bc["condition"]:
            case "eq":
                result = value1 == value2
                if not expr is None:
                    self.method_stack[-1].linear_constraint_stack.append(expr2+'=='+expr)
                else:
                    self.method_stack[-1].linear_constraint_stack.append(expr2+'=='+value1)
            case "ne":
                result = value1 != value2
                if not expr is None:
                    self.method_stack[-1].linear_constraint_stack.append(expr2+'!='+expr)
                else:
                    self.method_stack[-1].linear_constraint_stack.append(expr2+'!='+value1)
            case "lt":
                result = value1 < value2
                if not expr is None:
                    self.method_stack[-1].linear_constraint_stack.append(expr2+'<'+expr)
                else:
                    self.method_stack[-1].linear_constraint_stack.append(expr2+'<'+value1)
            case "ge":
                result = value1 >= value2
                if not expr is None:
                    self.method_stack[-1].linear_constraint_stack.append(expr2+'>='+expr)
                else:
                    self.method_stack[-1].linear_constraint_stack.append(expr2+'>='+value1)
            case "gt":
                result = value1 > value2
                if not expr is None:
                    self.method_stack[-1].linear_constraint_stack.append(expr2+'>'+expr)
                else:
                    self.method_stack[-1].linear_constraint_stack.append(expr2+'>'+value1)
            case "le":
                result = value1 <= value2
                if not expr is None:
                    self.method_stack[-1].linear_constraint_stack.append(expr2+'<='+expr)
                else:
                    self.method_stack[-1].linear_constraint_stack.append(expr2+'<='+value1)
            case _:
                self.done = f"can't handle {
                    bc['condition']!r} for if operations"
        if result:
            self.method_stack[-1].pc = bc["target"]
        else:
            self.method_stack[-1].pc += 1
    
if __name__ == "__main__":
        methodid = utils.MethodId.parse(sys.argv[1])
        inputs = utils.InputParser.parse(sys.argv[2])
        method = methodid.load()
        # Convert all inputs to integers
        inputs = [[l.tolocal() for l in i.value] if isinstance(
            i, utils.IntListValue) or isinstance(i, utils.CharListValue) else i.tolocal() for i in inputs]
        interpreter = SymbolicInterpreter(
            # heap=deque(),
            method_stack=deque(
                [ChildMethod(method["code"]["bytecode"], inputs, [], 0)])
        )
        print(interpreter.interpret())    
