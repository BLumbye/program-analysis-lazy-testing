import logging as l
from collections import deque
from typing import override

from common.common import CONST_ASSERTION_DISABLED, CONST_ZERO, constant_name
from common.codebase import *
from common.binary_expression import *
from simple_interpreter import SimpleInterpreter, Method

l.basicConfig(level=l.DEBUG, format="%(message)s")

class SymbolicInterpreter(SimpleInterpreter):

    def __init__(self, codebase: Codebase, method_stack: deque[Method]):
        super().__init__(codebase, method_stack)  # Pass required args to SimpleInterpreter

    def get_cache_id(self) -> int:
        cache_id = self._next_cache_ID 
        self._next_cache_ID += 1
        return cache_id

    def falsify_expr(self, e: BinaryExpr) -> BinaryExpr:
        return BinaryExpr(e, BinaryOp.EQ, CONST_ZERO, self.get_cache_id())
    
    @override
    def debug_step(self, next):
        super().debug_step(next)
        l.debug(f"  LINEAR CONSTRAINT: {self.linear_constraint_stack}")
    
    @override
    def step_get(self, bc):
        if bc["field"]["name"] == CONST_ASSERTION_DISABLED:
            self.current_method().stack.append((0, CONST_ASSERTION_DISABLED))
        else:
            self.done = f"can't handle get operations"

    @override
    def step_push(self,bc):
        expr = constant_name(bc['offset'], self.current_method().class_name, self.current_method().name)
        self.constant_dependencies.add(expr)
        
        if bc["value"] == None:
            self.current_method().stack.append((None, expr))
        else:
            self.current_method().stack.append((bc["value"]["value"], expr))

    @override
    def step_load(self, bc):
        value, expr = self.current_method().locals[bc["index"]]
        self.current_method().stack.append((value, expr))

    @override
    def step_binary(self, bc):
        value2, expr2 = self.current_method().stack.pop()
        value1, expr = self.current_method().stack.pop()
        bc_operant = bc["operant"]

        if value2 == 0 and bc_operant in ["div", "rem"]:
            # If we fail the same way, don't run again
            self.linear_constraint_stack.append(BinaryExpr(value2, BinaryOp.EQ, CONST_ZERO, self.get_cache_id()))
            self.done = "divide by zero"

        if (operant := BINARY_OPERATION_HANDLERS.get(bc_operant)) is not None:
            result, opr = operant(value1, value2)
        
            new_expr = BinaryExpr(expr, opr, expr2, self.get_cache_id())
            self.current_method().stack.append((result, new_expr))
        else:
            self.done = f"can't handle {bc_operant!r} for binary operations"
    
    @override
    def step_store(self, bc):
        while (len(self.current_method().locals) <= bc["index"]):
            self.current_method().locals.append((0, CONST_ZERO))
        
        elem = self.current_method().stack.pop()
        self.current_method().locals[bc["index"]] = elem
    
    @override
    def step_cast(self, bc):
        cast_type = bc['to']
        value, expr = self.current_method().stack.pop()
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
  
        self.current_method().stack.append((new_value, expr))

    def __if(self, bc, inst_name, elem1, elem2):
        value1, expr1 = elem1
        value2, expr2 = elem2
        bc_condition = bc["condition"]
        
        if (cond := IF_CONDITION_HANDLERS.get(bc_condition)) is not None:
            result, opr = cond(value1, value2)
            new_expr = BinaryExpr(expr1, opr, expr2, self.get_cache_id())

            if result:
                self.current_method().pc = bc["target"]
            else:
                new_expr = self.falsify_expr(new_expr)
                
            self.linear_constraint_stack.append(new_expr)
        else:
            self.done = f"can't handle {bc_condition!r} for {inst_name} operations"

    @override
    def step_ifz(self, bc):
        elem = self.current_method().stack.pop()
        self.__if(bc, "ifz", elem, (0, CONST_ZERO))

    @override
    def step_if(self, bc):
        elem2 = self.current_method().stack.pop()
        elem1 = self.current_method().stack.pop()
        self.__if(bc, "if", elem1, elem2)
