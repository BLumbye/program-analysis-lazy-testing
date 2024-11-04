import re
from common import constant_name, function_name, Expr, BinaryExpr, BinaryOp
from collections import deque
from typing import override
from interpreter import SimpleInterpreter, Method
from dataclasses import dataclass
from pathlib import Path
import sys
import logging
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
    class_name: str
    function_name: str
    cacheID: int
    def __init__(self, class_name: str, method_name: str, method_stack: deque[ChildMethod]):
        super().__init__(method_stack=method_stack)  # Pass required args to SimpleInterpreter
        self.class_name = class_name
        self.function_name = method_name
        self.cacheID=0

    @override
    def interpret(self, limit=1000):
        l.debug(inputs)
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
    def step_get(self, bc):
        if bc["field"]["name"] == "$assertionsDisabled":
            self.method_stack[-1].symbolic_stack.append((0,constant_name(bc['offset'],self.class_name,function_name(self.class_name,self.function_name))))
            self.method_stack[-1].pc += 1
        else:
            self.done = f"can't handle get operations"

    @override
    def step_push(self,bc):
        
        expr = constant_name(bc['offset'], self.class_name, function_name(self.class_name, self.function_name))
        if bc["value"] == None:
            self.method_stack[-1].stack.append(None)
            
            self.method_stack[-1].symbolic_stack.append((None,expr))
        else:
            self.method_stack[-1].stack.append(bc["value"]["value"])
            self.method_stack[-1].symbolic_stack.append((bc["value"]["value"],expr))
           
        
        self.method_stack[-1].pc += 1

    @override
    def step_load(self, bc):
       
        value = self.method_stack[-1].locals[bc["index"]]
        expr = constant_name(bc['offset'], self.class_name, function_name(self.class_name, self.function_name))
        self.method_stack[-1].symbolic_stack.append((value,expr))
        self.method_stack[-1].pc += 1

    @override
    def step_binary(self, bc):
        value2,expr2 = self.method_stack[-1].symbolic_stack.pop()
        value1,expr = self.method_stack[-1].symbolic_stack.pop()
        match bc["operant"]:
            case "add":
                new_expr = expr+'+'+expr2
                new_expr = BinaryExpr(expr, expr2, BinaryOp.ADD,self.cacheID)
                self.method_stack[-1].symbolic_stack.append((value1 + value2,new_expr))
            case "sub":
                new_expr = BinaryExpr(expr, expr2, BinaryOp.SUB,self.cacheID)
                self.method_stack[-1].symbolic_stack.append((value1 - value2,new_expr))
            case "mul":
                new_expr = BinaryExpr(expr, expr2, BinaryOp.MUL,self.cacheID)
                self.method_stack[-1].symbolic_stack.append((value1 * value2,new_expr))
            case "div":
                if value2 == 0:
                    self.done = "divide by zero"
                else:
                    if bc["type"] == "int":
                        new_expr = BinaryExpr(expr, expr2, BinaryOp.DIV,self.cacheID)
                        self.method_stack[-1].symbolic_stack.append((value1 // value2,new_expr))
                    else:
                        new_expr = BinaryExpr(expr, expr2, BinaryOp.DIV,self.cacheID)
                        self.method_stack[-1].symbolic_stack.append((value1 / value2,new_expr))
            case "rem":
                if value2 == 0:
                    self.done = "divide by zero"
                else:
                    new_expr = BinaryExpr(expr, expr2, BinaryOp.REM,self.cacheID)
                    self.method_stack[-1].symbolic_stack.append((value1 % value2,new_expr))
        self.cacheID+=1
        self.method_stack[-1].pc += 1
    
    @override
    def step_store(self, bc):
        while (len(self.method_stack[-1].locals) <= bc["index"]):
            self.method_stack[-1].locals.append(0)
        
        value,_=self.method_stack[-1].symbolic_stack.pop()
        self.method_stack[-1].locals[bc["index"]] = value
        self.method_stack[-1].pc += 1

    @override
    def step_ifz(self, bc):
        value,expr = self.method_stack[-1].symbolic_stack.pop()
    
        
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
        value2,expr2 = self.method_stack[-1].symbolic_stack.pop() 
        value1,expr = self.method_stack[-1].symbolic_stack.pop()
      
        result = False
        match bc["condition"]:
            case "eq":
                result = value1 == value2
                self.method_stack[-1].linear_constraint_stack.append(expr2+'=='+expr)
                
            case "ne":
                result = value1 != value2
                self.method_stack[-1].linear_constraint_stack.append(expr2+'!='+expr)
                
            case "lt":
                result = value1 < value2
                self.method_stack[-1].linear_constraint_stack.append(expr2+'<'+expr)
              
            case "ge":
                result = value1 >= value2
                self.method_stack[-1].linear_constraint_stack.append(expr2+'>='+expr)

            case "gt":
                result = value1 > value2
                self.method_stack[-1].linear_constraint_stack.append(expr2+'>'+expr)
        
            case "le":
                result = value1 <= value2
                self.method_stack[-1].linear_constraint_stack.append(expr2+'<='+expr)
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
        
        match = re.search(r"cases\.(\w+)\.(\w+)", sys.argv[1])
        if match:
            class_name = match.group(1)
            method_name = match.group(2)
        # Convert all inputs to integers
        inputs = [[l.tolocal() for l in i.value] if isinstance(
            i, utils.IntListValue) or isinstance(i, utils.CharListValue) else i.tolocal() for i in inputs]
        interpreter = SymbolicInterpreter( class_name = class_name, method_name = method_name,
            # heap=deque(),
            method_stack=deque(
                [ChildMethod(method["code"]["bytecode"], inputs, [], 0)])
        )
        print(interpreter.interpret())    
