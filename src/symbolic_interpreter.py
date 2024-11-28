import logging as l
from collections import deque
from typing import override, Optional

from common.common import CONST_ZERO, constant_name
from common.codebase import *
from common.expressions import *
from simple_interpreter import SimpleInterpreter, Method, set_should_log

l.basicConfig(level=l.DEBUG, format="%(message)s")

class SymbolicInterpreter(SimpleInterpreter):

    def __init__(self, codebase: Codebase, method_stack: deque[Method]):
        super().__init__(codebase, method_stack)  # Pass required args to SimpleInterpreter
        self._found_constraints = set()
        # set_should_log(True)

        for class_name, fields in self.fields.items():
            for field_name, field_value in fields.items():
                fields[field_name] = (field_value, constant_name(field_name, class_name))
        
    def __get_cache_id(self) -> int:
        cache_id = self._next_cache_ID 
        self._next_cache_ID += 1
        return cache_id
    
    def __add_constraint(self, expr: BinaryExpr) -> None:
        self._constraints.append(expr)
        self._cache_size = max(self._cache_size, expr.cache_id + 1)

    def __falsify_expr(self, e: BinaryExpr) -> BinaryExpr:
        return BinaryExpr(e, BinaryOp.EQ, CONST_ZERO, self.__get_cache_id())
    
    @override
    def debug_step(self, next):
        super().debug_step(next)
        l.debug(f"  CONSTRAINTS: {self._constraints}")
        l.debug(f"  NEXT CACHE ID: {self._next_cache_ID}")

    @override
    def step_push(self, bc):
        expr = constant_name(self.current_method().pc - 1, self.current_method().class_name, self.current_method().name)
        self.constant_dependencies.add(expr)
        self.current_method().stack.append((bc["value"]["value"], expr) if bc["value"] else (None, expr))

    @override
    def step_load(self, bc):
        value, expr = self.current_method().locals[bc["index"]]
        self.current_method().stack.append((value, expr))

    @override
    def step_incr(self, bc):
        value, expr = self.current_method().locals[bc["index"]]
        amount_expr = constant_name(self.current_method().pc - 1, self.current_method().class_name, self.current_method().name)
        self.constant_dependencies.add(amount_expr)

        new_expr = BinaryExpr(expr, BinaryOp.ADD, amount_expr, self.__get_cache_id())
        self.current_method().locals[bc["index"]] = (value + bc["amount"], new_expr)

    @override
    def step_binary(self, bc):
        value2, expr2 = self.current_method().stack.pop()
        value1, expr = self.current_method().stack.pop()
        bc_operant = bc["operant"]

        if bc_operant in ["div", "rem"]:
            if value2 == 0:
                # If we fail the same way, don't run again
                self.__add_constraint(BinaryExpr(expr2, BinaryOp.EQ, CONST_ZERO, self.__get_cache_id()))
                self.done = "divide by zero"
                return
        
            self.__add_constraint(BinaryExpr(expr2, BinaryOp.NE, CONST_ZERO, self.__get_cache_id()))

        if (operant := BINARY_OPERATION_HANDLERS.get(bc_operant)) is not None:
            result, opr = operant(value1, value2)
        
            new_expr = BinaryExpr(expr, opr, expr2, self.__get_cache_id())
            self.current_method().stack.append((result, new_expr))
        else:
            self.done = f"can't handle {bc_operant!r} for binary operations"

    @override
    def step_negate(self, _):
        value, expr = self.current_method().stack.pop()
        new_expr = BinaryExpr(CONST_ZERO, BinaryOp.SUB, expr, self.__get_cache_id())
        self.current_method().stack.append((-value, new_expr))
    
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
            new_expr = BinaryExpr(expr1, opr, expr2, self.__get_cache_id())

            if result:
                self.current_method().pc = bc["target"]
            else:
                new_expr = self.__falsify_expr(new_expr)
                
            self.__add_constraint(new_expr)
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

    def _check_array(self, array: Optional[list[int]], index: Optional[int], 
                     array_expr: ArrayExpr | str, index_expr: Optional[Expr]) -> bool:
        if array is None:
            self.__add_constraint(BinaryExpr(array_expr, BinaryOp.EQ, None, self.__get_cache_id()))
            self.done = "null pointer"
            return False
        
        if index is not None and index >= len(array):
            self.__add_constraint(BinaryExpr(index_expr, BinaryOp.GE, array_expr.size, self.__get_cache_id()))
            self.done = "out of bounds"
            return False

        return True

    @override
    def step_newarray(self, bc):
        if bc["dim"] != 1:
            self.done = f"can't handle multi-dimensional arrays"
        elif bc["type"] != "int":
            self.done = f"can't handle {bc['type']!r} for newarray operations"
        else:
            size, expr = self.current_method().stack.pop()
            self.current_method().stack.append(([0] * size, ArrayExpr(expr, [CONST_ZERO] * size)))

    @override
    def step_array_store(self, _):
        value, expr = self.current_method().stack.pop()
        index, index_expr = self.current_method().stack.pop()
        array_value, array_expr = self.current_method().stack.pop()
        if not self._check_array(array_value, index, array_expr, index_expr):
            return
        # Is it the same index as previously?
        self.__add_constraint(BinaryExpr(index, BinaryOp.EQ, index_expr, self.__get_cache_id()))
        # Is the value still stored within the array?
        self.__add_constraint(BinaryExpr(index_expr, BinaryOp.LT, array_expr.size, self.__get_cache_id()))
        array_value[index] = value
        array_expr.array[index] = expr

    @override
    def step_array_load(self, _):
        index, index_expr = self.current_method().stack.pop()
        array_value, array_expr = self.current_method().stack.pop()
        print(index, index_expr, array_value, array_expr)
        print(self.fields)
        if not self._check_array(array_value, index, array_expr, index_expr):
            return
        # Is it the same index as previously?
        self.__add_constraint(BinaryExpr(index, BinaryOp.EQ, index_expr, self.__get_cache_id()))
        # Is the value fetched from within the array?
        self.__add_constraint(BinaryExpr(index_expr, BinaryOp.LT, array_expr.size, self.__get_cache_id()))
        self.current_method().stack.append((array_value[index], array_expr.array[index]))

    @override
    def step_arraylength(self, _):
        array_value, array_expr = self.current_method().stack.pop()
        if not self._check_array(array_value, None, array_expr, None):
            return
        self.current_method().stack.append((len(array_value), array_expr.size))
