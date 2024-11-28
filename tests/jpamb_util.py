import os
import json
import re
from typing import Generator
from dataclasses import dataclass
from jpamb_utils import *
from common.common import *
from common.codebase import Codebase
from common.expressions import *

def load_jpamb_suite() -> Codebase:
    bytecode = dict()
    json_path = os.path.join(os.path.dirname(__file__), "jpamb", "decompiled")
    for name, file_path in all_file_paths(json_path):
        with open(file_path, 'r') as file:
            bytecode[name] = json.load(file)

    return Codebase(bytecode)

@dataclass(frozen=True)
class Case:
    id: int
    class_name: str
    name: str
    locals: list
    response: str

def convert_jpamb_input(input) -> int | list[int]:
    match input:
        case IntValue():
            return input.tolocal()
        case BoolValue() | CharValue():
            return convert_jpamb_input(input.tolocal())
        case IntListValue() | CharListValue():
            return list(map(convert_jpamb_input, input.tolocal()))
        case _:
            raise ValueError(f"Unexpected input value: {input!r}")

# taken from jpamb/bin/test.py
def parse_case(line, id) -> Case:
    if not (m := re.match(r"([^ ]*) +(\([^)]*\)) -> (.*)", line)):
        raise ValueError(f"Unexpected line: {line!r}")
    
    method_id = MethodId.parse(m.group(1))
    inputs = list(map(convert_jpamb_input, InputParser.parse(m.group(2))))

    return Case(id, method_id.class_name.replace(".", "/"), method_id.method_name, inputs, m.group(3))

def prepare_cases() -> Generator[Case, None, None]:
    cases_path = os.path.join(os.path.dirname(__file__), "jpamb", "stats", "cases.txt")
    next_id = 0
    with open(cases_path, 'r') as file:
        for ls in file.readlines():
            id = next_id
            next_id += 1
            yield parse_case(ls[:-1], id)

@dataclass(frozen=True)
class ExpectedResult:
    depends_on_methods: list[str]
    depends_on_constants: list[str]
    constraints: list[BinaryExpr]
    cache_size: int

# Based on jpamb/stats/cases.txt
# Cases were it was deemed infeasible to manually 
# write the symbolic expression only contains dependencies and constants
JPAMB_EXPECTED_RESULTS = {
    0 : ExpectedResult(
            ["jpamb/cases/Arrays:arrayContent"], 
            [
                CONST_ASSERTION_DISABLED,
                "jpamb/cases/Arrays:arrayContent:0",
                "jpamb/cases/Arrays:arrayContent:3",
                "jpamb/cases/Arrays:arrayContent:4",
                "jpamb/cases/Arrays:arrayContent:7",
                "jpamb/cases/Arrays:arrayContent:8",
                "jpamb/cases/Arrays:arrayContent:11",
                "jpamb/cases/Arrays:arrayContent:12",
                "jpamb/cases/Arrays:arrayContent:15",
                "jpamb/cases/Arrays:arrayContent:16",
                "jpamb/cases/Arrays:arrayContent:19",
                "jpamb/cases/Arrays:arrayContent:20",
                "jpamb/cases/Arrays:arrayContent:23"
            ],
            [
                BinaryExpr(0, BinaryOp.EQ, "jpamb/cases/Arrays:arrayContent:3", 0),
                BinaryExpr("jpamb/cases/Arrays:arrayContent:3", BinaryOp.LT, "jpamb/cases/Arrays:arrayContent:0", 1),
                BinaryExpr(1, BinaryOp.EQ, "jpamb/cases/Arrays:arrayContent:7", 2),
                BinaryExpr("jpamb/cases/Arrays:arrayContent:7", BinaryOp.LT, "jpamb/cases/Arrays:arrayContent:0", 3),
                BinaryExpr(2, BinaryOp.EQ, "jpamb/cases/Arrays:arrayContent:11", 4),
                BinaryExpr("jpamb/cases/Arrays:arrayContent:11", BinaryOp.LT, "jpamb/cases/Arrays:arrayContent:0", 5),
                BinaryExpr(3, BinaryOp.EQ, "jpamb/cases/Arrays:arrayContent:15", 6),
                BinaryExpr("jpamb/cases/Arrays:arrayContent:15", BinaryOp.LT, "jpamb/cases/Arrays:arrayContent:0", 7),
                BinaryExpr(4, BinaryOp.EQ, "jpamb/cases/Arrays:arrayContent:19", 8),
                BinaryExpr("jpamb/cases/Arrays:arrayContent:19", BinaryOp.LT, "jpamb/cases/Arrays:arrayContent:0", 9),
                BinaryExpr(BinaryExpr("jpamb/cases/Arrays:arrayContent:23", BinaryOp.GE, "jpamb/cases/Arrays:arrayContent:0", 10), BinaryOp.EQ, CONST_ZERO, 11),
                BinaryExpr(BinaryExpr(CONST_ASSERTION_DISABLED, BinaryOp.NE, CONST_ZERO, 12), BinaryOp.EQ, CONST_ZERO, 13),
                BinaryExpr(BinaryExpr("jpamb/cases/Arrays:arrayContent:23", BinaryOp.GT, CONST_ZERO, 14), BinaryOp.EQ, CONST_ZERO, 15)
            ], 
            16
        ),
    1 : ExpectedResult(
            ["jpamb/cases/Arrays:arrayInBounds"], 
            [
                "jpamb/cases/Arrays:arrayInBounds:0",
                "jpamb/cases/Arrays:arrayInBounds:3",
                "jpamb/cases/Arrays:arrayInBounds:4",
                "jpamb/cases/Arrays:arrayInBounds:7",
                "jpamb/cases/Arrays:arrayInBounds:8",
                "jpamb/cases/Arrays:arrayInBounds:12",
                "jpamb/cases/Arrays:arrayInBounds:13"
            ], 
            [
                BinaryExpr(0, BinaryOp.EQ, "jpamb/cases/Arrays:arrayInBounds:3", 0),
                BinaryExpr("jpamb/cases/Arrays:arrayInBounds:3", BinaryOp.LT, "jpamb/cases/Arrays:arrayInBounds:0", 1),
                BinaryExpr(1, BinaryOp.EQ, "jpamb/cases/Arrays:arrayInBounds:7", 2),
                BinaryExpr("jpamb/cases/Arrays:arrayInBounds:7", BinaryOp.LT, "jpamb/cases/Arrays:arrayInBounds:0", 3),
                BinaryExpr(1, BinaryOp.EQ, "jpamb/cases/Arrays:arrayInBounds:12", 4),
                BinaryExpr("jpamb/cases/Arrays:arrayInBounds:12", BinaryOp.LT, "jpamb/cases/Arrays:arrayInBounds:0", 5),
            ],
            6
        ),
    2 : ExpectedResult(
            ["jpamb/cases/Arrays:arrayIsNull"], 
            [
                "jpamb/cases/Arrays:arrayIsNull:0",
                "jpamb/cases/Arrays:arrayIsNull:3",
                "jpamb/cases/Arrays:arrayIsNull:4"
            ], 
            [BinaryExpr("jpamb/cases/Arrays:arrayIsNull:0", BinaryOp.EQ, None, 0)], 
            1
        ),
    3 : ExpectedResult(
            ["jpamb/cases/Arrays:arrayIsNullLength"], 
            [
                CONST_ASSERTION_DISABLED,
                "jpamb/cases/Arrays:arrayIsNullLength:0"
            ], 
            [
               BinaryExpr(BinaryExpr(CONST_ASSERTION_DISABLED, BinaryOp.NE, CONST_ZERO, 0), BinaryOp.EQ, CONST_ZERO, 1),
               BinaryExpr("jpamb/cases/Arrays:arrayIsNullLength:0", BinaryOp.EQ, None, 2)
            ], 
            3
        ),
    4 : ExpectedResult(
            ["jpamb/cases/Arrays:arrayLength"], 
            [
                CONST_ASSERTION_DISABLED,
                "jpamb/cases/Arrays:arrayLength:0",
                "jpamb/cases/Arrays:arrayLength:3",
                "jpamb/cases/Arrays:arrayLength:4",
                "jpamb/cases/Arrays:arrayLength:7",
                "jpamb/cases/Arrays:arrayLength:8",
                "jpamb/cases/Arrays:arrayLength:15"
            ], 
            [
                BinaryExpr(0, BinaryOp.EQ, "jpamb/cases/Arrays:arrayLength:3", 0),
                BinaryExpr("jpamb/cases/Arrays:arrayLength:3", BinaryOp.LT, "jpamb/cases/Arrays:arrayLength:0", 1),
                BinaryExpr(1, BinaryOp.EQ, "jpamb/cases/Arrays:arrayLength:7", 2),
                BinaryExpr("jpamb/cases/Arrays:arrayLength:7", BinaryOp.LT, "jpamb/cases/Arrays:arrayLength:0", 3),
                BinaryExpr(BinaryExpr(CONST_ASSERTION_DISABLED, BinaryOp.NE, CONST_ZERO, 4), BinaryOp.EQ, CONST_ZERO, 5),
                BinaryExpr("jpamb/cases/Arrays:arrayLength:0", BinaryOp.EQ, "jpamb/cases/Arrays:arrayLength:15", 6)
            ], 
            7
        ),
    5 : ExpectedResult(
            ["jpamb/cases/Arrays:arrayNotEmpty"], 
            [CONST_ASSERTION_DISABLED], 
            [
                BinaryExpr(BinaryExpr(CONST_ASSERTION_DISABLED, BinaryOp.NE, CONST_ZERO, 0), BinaryOp.EQ, CONST_ZERO, 1),
                BinaryExpr("jpamb/cases/Arrays:arrayNotEmpty:input:a:size:1", BinaryOp.GT, CONST_ZERO, 2)
            ], 
            3
        ),
    6 : ExpectedResult(
            ["jpamb/cases/Arrays:arrayNotEmpty"], 
            [CONST_ASSERTION_DISABLED], 
            [
                BinaryExpr(BinaryExpr(CONST_ASSERTION_DISABLED, BinaryOp.NE, CONST_ZERO, 0), BinaryOp.EQ, CONST_ZERO, 1),
                BinaryExpr(BinaryExpr("jpamb/cases/Arrays:arrayNotEmpty:input:a:size:0", BinaryOp.GT, CONST_ZERO, 2), BinaryOp.EQ, CONST_ZERO, 3)
            ], 
            4
        ),
    7 : ExpectedResult(
            ["jpamb/cases/Arrays:arrayOutOfBounds"], 
            [
                "jpamb/cases/Arrays:arrayOutOfBounds:0",
                "jpamb/cases/Arrays:arrayOutOfBounds:3",
                "jpamb/cases/Arrays:arrayOutOfBounds:4",
                "jpamb/cases/Arrays:arrayOutOfBounds:7",
                "jpamb/cases/Arrays:arrayOutOfBounds:8",
                "jpamb/cases/Arrays:arrayOutOfBounds:12",
                "jpamb/cases/Arrays:arrayOutOfBounds:13"
            ], 
            [
                BinaryExpr(0, BinaryOp.EQ, "jpamb/cases/Arrays:arrayOutOfBounds:3", 0),
                BinaryExpr("jpamb/cases/Arrays:arrayOutOfBounds:3", BinaryOp.LT, "jpamb/cases/Arrays:arrayOutOfBounds:0", 1),
                BinaryExpr(1, BinaryOp.EQ, "jpamb/cases/Arrays:arrayOutOfBounds:7", 2),
                BinaryExpr("jpamb/cases/Arrays:arrayOutOfBounds:7", BinaryOp.LT, "jpamb/cases/Arrays:arrayOutOfBounds:0", 3),
                BinaryExpr("jpamb/cases/Arrays:arrayOutOfBounds:12", BinaryOp.GE, "jpamb/cases/Arrays:arrayOutOfBounds:0", 4),
            ], 
            5
        ),
    8 : ExpectedResult(
            ["jpamb/cases/Arrays:arraySometimesNull"], 
            [
                "jpamb/cases/Arrays:arraySometimesNull:0",
                "jpamb/cases/Arrays:arraySometimesNull:3",
                "jpamb/cases/Arrays:arraySometimesNull:5",
                "jpamb/cases/Arrays:arraySometimesNull:8",
                "jpamb/cases/Arrays:arraySometimesNull:13",
                "jpamb/cases/Arrays:arraySometimesNull:14"
            ], 
            [
                BinaryExpr(BinaryExpr("jpamb/cases/Arrays:arraySometimesNull:input:a:0", BinaryOp.GE, "jpamb/cases/Arrays:arraySometimesNull:3", 0), BinaryOp.EQ, CONST_ZERO, 1),
                BinaryExpr(0, BinaryOp.EQ, "jpamb/cases/Arrays:arraySometimesNull:8", 2),
                BinaryExpr("jpamb/cases/Arrays:arraySometimesNull:8", BinaryOp.LT, "jpamb/cases/Arrays:arraySometimesNull:5", 3),
                BinaryExpr("jpamb/cases/Arrays:arraySometimesNull:13", BinaryOp.GE, "jpamb/cases/Arrays:arraySometimesNull:5", 4)
            ], 
            5
        ),
    9 : ExpectedResult(
            ["jpamb/cases/Arrays:arraySometimesNull"], 
            [
                "jpamb/cases/Arrays:arraySometimesNull:0",
                "jpamb/cases/Arrays:arraySometimesNull:3",
                "jpamb/cases/Arrays:arraySometimesNull:13",
                "jpamb/cases/Arrays:arraySometimesNull:14"
            ], 
            [
                BinaryExpr("jpamb/cases/Arrays:arraySometimesNull:input:a:11", BinaryOp.GE, "jpamb/cases/Arrays:arraySometimesNull:3", 0),
                BinaryExpr("jpamb/cases/Arrays:arraySometimesNull:0", BinaryOp.EQ, None, 1)
            ],
            2
        ),
    10 : ExpectedResult(
            ["jpamb/cases/Arrays:arraySpellsHello"], 
            [
                CONST_ASSERTION_DISABLED,
                "jpamb/cases/Arrays:arraySpellsHello:3",
                "jpamb/cases/Arrays:arraySpellsHello:5",
                "jpamb/cases/Arrays:arraySpellsHello:8",
                "jpamb/cases/Arrays:arraySpellsHello:10",
                "jpamb/cases/Arrays:arraySpellsHello:13",
                "jpamb/cases/Arrays:arraySpellsHello:15",
                "jpamb/cases/Arrays:arraySpellsHello:18",
                "jpamb/cases/Arrays:arraySpellsHello:20",
                "jpamb/cases/Arrays:arraySpellsHello:23",
                "jpamb/cases/Arrays:arraySpellsHello:25"
            ], 
            [
                BinaryExpr(BinaryExpr(CONST_ASSERTION_DISABLED, BinaryOp.NE, CONST_ZERO, 0), BinaryOp.EQ, CONST_ZERO, 1),
                BinaryExpr(0, BinaryOp.EQ, "jpamb/cases/Arrays:arraySpellsHello:3", 2),
                BinaryExpr("jpamb/cases/Arrays:arraySpellsHello:3", BinaryOp.LT, "jpamb/cases/Arrays:arraySpellsHello:input:a:size:5", 3),
                BinaryExpr(BinaryExpr("jpamb/cases/Arrays:arraySpellsHello:input:a:0:104", BinaryOp.NE, "jpamb/cases/Arrays:arraySpellsHello:5", 4), BinaryOp.EQ, CONST_ZERO, 5),
                BinaryExpr(1, BinaryOp.EQ, "jpamb/cases/Arrays:arraySpellsHello:8", 6),
                BinaryExpr("jpamb/cases/Arrays:arraySpellsHello:8", BinaryOp.LT, "jpamb/cases/Arrays:arraySpellsHello:input:a:size:5", 7),
                BinaryExpr(BinaryExpr("jpamb/cases/Arrays:arraySpellsHello:input:a:1:101", BinaryOp.NE, "jpamb/cases/Arrays:arraySpellsHello:10", 8), BinaryOp.EQ, CONST_ZERO, 9),
                BinaryExpr(2, BinaryOp.EQ, "jpamb/cases/Arrays:arraySpellsHello:13", 10),
                BinaryExpr("jpamb/cases/Arrays:arraySpellsHello:13", BinaryOp.LT, "jpamb/cases/Arrays:arraySpellsHello:input:a:size:5", 11),
                BinaryExpr(BinaryExpr("jpamb/cases/Arrays:arraySpellsHello:input:a:2:108", BinaryOp.NE, "jpamb/cases/Arrays:arraySpellsHello:15", 12), BinaryOp.EQ, CONST_ZERO, 13),
                BinaryExpr(3, BinaryOp.EQ, "jpamb/cases/Arrays:arraySpellsHello:18", 14),
                BinaryExpr("jpamb/cases/Arrays:arraySpellsHello:18", BinaryOp.LT, "jpamb/cases/Arrays:arraySpellsHello:input:a:size:5", 15),
                BinaryExpr(BinaryExpr("jpamb/cases/Arrays:arraySpellsHello:input:a:3:108", BinaryOp.NE, "jpamb/cases/Arrays:arraySpellsHello:20", 16), BinaryOp.EQ, CONST_ZERO, 17),
                BinaryExpr(4, BinaryOp.EQ, "jpamb/cases/Arrays:arraySpellsHello:23", 18),
                BinaryExpr("jpamb/cases/Arrays:arraySpellsHello:23", BinaryOp.LT, "jpamb/cases/Arrays:arraySpellsHello:input:a:size:5", 19),
                BinaryExpr("jpamb/cases/Arrays:arraySpellsHello:input:a:4:111", BinaryOp.EQ, "jpamb/cases/Arrays:arraySpellsHello:25", 20)
            ],
            21
        ),
    11 : ExpectedResult(
            ["jpamb/cases/Arrays:arraySpellsHello"], 
            [
                CONST_ASSERTION_DISABLED,
                "jpamb/cases/Arrays:arraySpellsHello:3",
                "jpamb/cases/Arrays:arraySpellsHello:5"
            ], 
            [
                BinaryExpr(BinaryExpr(CONST_ASSERTION_DISABLED, BinaryOp.NE, CONST_ZERO, 0), BinaryOp.EQ, CONST_ZERO, 1),
                BinaryExpr(0, BinaryOp.EQ, "jpamb/cases/Arrays:arraySpellsHello:3", 2),
                BinaryExpr("jpamb/cases/Arrays:arraySpellsHello:3", BinaryOp.LT, "jpamb/cases/Arrays:arraySpellsHello:input:a:size:1", 3),
                BinaryExpr("jpamb/cases/Arrays:arraySpellsHello:input:a:0:120", BinaryOp.NE, "jpamb/cases/Arrays:arraySpellsHello:5", 4),
            ],
            5
        ),
    12 : ExpectedResult(
            ["jpamb/cases/Arrays:arraySpellsHello"], 
            [
                CONST_ASSERTION_DISABLED,
                "jpamb/cases/Arrays:arraySpellsHello:3"
            ], 
            [
                BinaryExpr(BinaryExpr(CONST_ASSERTION_DISABLED, BinaryOp.NE, CONST_ZERO, 0), BinaryOp.EQ, CONST_ZERO, 1),
                BinaryExpr("jpamb/cases/Arrays:arraySpellsHello:3", BinaryOp.GE, "jpamb/cases/Arrays:arraySpellsHello:input:a:size:0", 2)
            ],
            3
        ),
    13 : ExpectedResult(
            ["jpamb/cases/Arrays:arraySumIsLarge"], 
            [
                CONST_ASSERTION_DISABLED,
                "jpamb/cases/Arrays:arraySumIsLarge:0",  # sum
                "jpamb/cases/Arrays:arraySumIsLarge:2",  # i
                "jpamb/cases/Arrays:arraySumIsLarge:14", # ++
                "jpamb/cases/Arrays:arraySumIsLarge:19"  # 300
            ], 
            [
                BinaryExpr(BinaryExpr("jpamb/cases/Arrays:arraySumIsLarge:2", BinaryOp.GE, "jpamb/cases/Arrays:arraySumIsLarge:input:a:size:3", 0), BinaryOp.EQ, CONST_ZERO, 1),
                BinaryExpr(0, BinaryOp.EQ, "jpamb/cases/Arrays:arraySumIsLarge:2", 2),
                BinaryExpr("jpamb/cases/Arrays:arraySumIsLarge:2", BinaryOp.LT, "jpamb/cases/Arrays:arraySumIsLarge:input:a:size:3", 3),

                BinaryExpr(BinaryExpr(BinaryExpr("jpamb/cases/Arrays:arraySumIsLarge:2", BinaryOp.ADD, "jpamb/cases/Arrays:arraySumIsLarge:14", 5), BinaryOp.GE, "jpamb/cases/Arrays:arraySumIsLarge:input:a:size:3", 6), BinaryOp.EQ, CONST_ZERO, 7),
                BinaryExpr(1, BinaryOp.EQ, BinaryExpr("jpamb/cases/Arrays:arraySumIsLarge:2", BinaryOp.ADD, "jpamb/cases/Arrays:arraySumIsLarge:14", 5), 8),
                BinaryExpr(BinaryExpr("jpamb/cases/Arrays:arraySumIsLarge:2", BinaryOp.ADD, "jpamb/cases/Arrays:arraySumIsLarge:14", 5), BinaryOp.LT, "jpamb/cases/Arrays:arraySumIsLarge:input:a:size:3", 9),

                BinaryExpr(BinaryExpr(BinaryExpr(BinaryExpr("jpamb/cases/Arrays:arraySumIsLarge:2", BinaryOp.ADD, "jpamb/cases/Arrays:arraySumIsLarge:14", 5), BinaryOp.ADD, "jpamb/cases/Arrays:arraySumIsLarge:14", 11), BinaryOp.GE, "jpamb/cases/Arrays:arraySumIsLarge:input:a:size:3", 12), BinaryOp.EQ, CONST_ZERO, 13),
                BinaryExpr(2, BinaryOp.EQ, BinaryExpr(BinaryExpr("jpamb/cases/Arrays:arraySumIsLarge:2", BinaryOp.ADD, "jpamb/cases/Arrays:arraySumIsLarge:14", 5), BinaryOp.ADD, "jpamb/cases/Arrays:arraySumIsLarge:14", 11), 14),
                BinaryExpr(BinaryExpr(BinaryExpr("jpamb/cases/Arrays:arraySumIsLarge:2", BinaryOp.ADD, "jpamb/cases/Arrays:arraySumIsLarge:14", 5), BinaryOp.ADD, "jpamb/cases/Arrays:arraySumIsLarge:14", 11), BinaryOp.LT, "jpamb/cases/Arrays:arraySumIsLarge:input:a:size:3", 15),

                BinaryExpr(BinaryExpr(BinaryExpr(BinaryExpr("jpamb/cases/Arrays:arraySumIsLarge:2", BinaryOp.ADD, "jpamb/cases/Arrays:arraySumIsLarge:14", 5), BinaryOp.ADD, "jpamb/cases/Arrays:arraySumIsLarge:14", 11), BinaryOp.ADD, "jpamb/cases/Arrays:arraySumIsLarge:14", 17), BinaryOp.GE, "jpamb/cases/Arrays:arraySumIsLarge:input:a:size:3", 18),
                BinaryExpr(BinaryExpr(CONST_ASSERTION_DISABLED, BinaryOp.NE, CONST_ZERO, 19), BinaryOp.EQ, CONST_ZERO, 20),
                BinaryExpr(BinaryExpr(BinaryExpr(BinaryExpr("jpamb/cases/Arrays:arraySumIsLarge:0", BinaryOp.ADD, "jpamb/cases/Arrays:arraySumIsLarge:input:a:0:50", 4), BinaryOp.ADD, "jpamb/cases/Arrays:arraySumIsLarge:input:a:1:100", 10), BinaryOp.ADD, "jpamb/cases/Arrays:arraySumIsLarge:input:a:2:200", 16), BinaryOp.GT, "jpamb/cases/Arrays:arraySumIsLarge:19", 21)
            ], 
            22
        ),
    14 : ExpectedResult(
            ["jpamb/cases/Arrays:arraySumIsLarge"], 
            [
                CONST_ASSERTION_DISABLED,
                "jpamb/cases/Arrays:arraySumIsLarge:0", # sum
                "jpamb/cases/Arrays:arraySumIsLarge:2", # i
                "jpamb/cases/Arrays:arraySumIsLarge:19" # 300
            ],
            [
                BinaryExpr("jpamb/cases/Arrays:arraySumIsLarge:2", BinaryOp.GE, "jpamb/cases/Arrays:arraySumIsLarge:input:a:size:0", 0),
                BinaryExpr(BinaryExpr(CONST_ASSERTION_DISABLED, BinaryOp.NE, CONST_ZERO, 1), BinaryOp.EQ, CONST_ZERO, 2),
                BinaryExpr(BinaryExpr("jpamb/cases/Arrays:arraySumIsLarge:0", BinaryOp.GT, "jpamb/cases/Arrays:arraySumIsLarge:19", 3), BinaryOp.EQ, CONST_ZERO, 4)
            ], 
            5
        ),
    15 : ExpectedResult(
            ["jpamb/cases/Arrays:binarySearch"], 
            [], 
            [], 
            0
        ),
    16 : ExpectedResult(
            ["jpamb/cases/Arrays:binarySearch"], 
            [], 
            [], 
            0
        ),
    17 : ExpectedResult(
            [
                "jpamb/cases/Calls:allPrimesArePositive", 
                "jpamb/cases/Calls:generatePrimeArray"
            ], 
            [], 
            [], 
            0
        ),
    18 : ExpectedResult(
            [
                "jpamb/cases/Calls:allPrimesArePositive", 
                "jpamb/cases/Calls:generatePrimeArray"
            ], 
            [], 
            [], 
            0
        ),
    19 : ExpectedResult(
            [
                "jpamb/cases/Calls:allPrimesArePositive", 
                "jpamb/cases/Calls:generatePrimeArray"
            ], 
            [], 
            [], 
            0
        ),
    20 : ExpectedResult(
            [
                "jpamb/cases/Calls:callsAssertFalse", 
                "jpamb/cases/Calls:assertFalse"
            ], 
            [CONST_ASSERTION_DISABLED], 
            [BinaryExpr(BinaryExpr(CONST_ASSERTION_DISABLED, BinaryOp.NE, CONST_ZERO, 0), BinaryOp.EQ, CONST_ZERO, 1)], 
            2
        ),
    21 : ExpectedResult(
            [
                "jpamb/cases/Calls:callsAssertFib", 
                "jpamb/cases/Calls:fib"
            ], 
            [
                CONST_ASSERTION_DISABLED,
                "jpamb/cases/Calls:callsAssertFib:4"
            ], 
            [
                BinaryExpr(BinaryExpr(CONST_ASSERTION_DISABLED, BinaryOp.NE, CONST_ZERO, 0), BinaryOp.EQ, CONST_ZERO, 1),
                BinaryExpr("jpamb/cases/Calls:callsAssertFib:input:a:0", BinaryOp.EQ, CONST_ZERO, 2),
                BinaryExpr(BinaryExpr("jpamb/cases/Calls:callsAssertFib:input:a:0", BinaryOp.EQ, "jpamb/cases/Calls:callsAssertFib:4", 3), BinaryOp.EQ, CONST_ZERO, 4)
            ], 
            5
        ),
    22 : ExpectedResult(
            [
                "jpamb/cases/Calls:callsAssertFib", 
                "jpamb/cases/Calls:fib"
            ], 
            [],
            [], 
            0
        ),
    23 : ExpectedResult(
            [
                "jpamb/cases/Calls:callsAssertIf", 
                "jpamb/cases/Calls:assertIf", 
                "jpamb/cases/Calls:assertFalse"
            ], 
            [CONST_ASSERTION_DISABLED], 
            [
                BinaryExpr("jpamb/cases/Calls:callsAssertIf:input:a:0", BinaryOp.EQ, CONST_ZERO, 0),
                BinaryExpr(BinaryExpr(CONST_ASSERTION_DISABLED, BinaryOp.NE, CONST_ZERO, 1), BinaryOp.EQ, CONST_ZERO, 2)
            ], 
            3
        ),
    24 : ExpectedResult(
            [
                "jpamb/cases/Calls:callsAssertIf", 
                "jpamb/cases/Calls:assertIf", 
                "jpamb/cases/Calls:assertTrue"
            ], 
            [], 
            [BinaryExpr(BinaryExpr("jpamb/cases/Calls:callsAssertIf:input:a:1", BinaryOp.EQ, CONST_ZERO, 0), BinaryOp.EQ, CONST_ZERO, 1)], 
            2
        ),
    25 : ExpectedResult(
            [
                "jpamb/cases/Calls:callsAssertIfWithTrue", 
                "jpamb/cases/Calls:assertIf", 
                "jpamb/cases/Calls:assertTrue"
            ], 
            ["jpamb/cases/Calls:callsAssertIfWithTrue:0"], 
            [BinaryExpr(BinaryExpr("jpamb/cases/Calls:callsAssertIfWithTrue:0", BinaryOp.EQ, CONST_ZERO, 0), BinaryOp.EQ, CONST_ZERO, 1)],
            2
        ),
    26 : ExpectedResult(
            [
                "jpamb/cases/Calls:callsAssertTrue", 
                "jpamb/cases/Calls:assertTrue"
            ], 
            [], 
            [], 
            0
        ),
    27 : ExpectedResult(
            ["jpamb/cases/Loops:forever"], 
            [], 
            [], 
            0
        ),
    28 : ExpectedResult(
            ["jpamb/cases/Loops:neverAsserts"], 
            ["jpamb/cases/Loops:neverAsserts:0"], 
            [], 
            0
        ),
    29 : ExpectedResult(
            ["jpamb/cases/Loops:neverDivides"], 
            ["jpamb/cases/Loops:neverDivides:0"], 
            [], 
            0
        ),
    30 : ExpectedResult(
            ["jpamb/cases/Loops:terminates"], 
            [
                CONST_ASSERTION_DISABLED,
                "jpamb/cases/Loops:terminates:0",
                "jpamb/cases/Loops:terminates:4"
            ], 
            [
                BinaryExpr("jpamb/cases/Loops:terminates:0", BinaryOp.EQ, CONST_ZERO, 1),
                BinaryExpr(BinaryExpr(CONST_ASSERTION_DISABLED, BinaryOp.NE, CONST_ZERO, 2), BinaryOp.EQ, CONST_ZERO, 3)
            ],
            4
        ),
    31 : ExpectedResult(
            ["jpamb/cases/Simple:assertBoolean"], 
            [CONST_ASSERTION_DISABLED],
            [
                BinaryExpr(BinaryExpr(CONST_ASSERTION_DISABLED, BinaryOp.NE, CONST_ZERO, 0), BinaryOp.EQ, CONST_ZERO, 1),
                BinaryExpr(BinaryExpr("jpamb/cases/Simple:assertBoolean:input:a:0", BinaryOp.NE, CONST_ZERO, 2), BinaryOp.EQ, CONST_ZERO, 3)
            ],
            4
        ),
    32 : ExpectedResult(
            ["jpamb/cases/Simple:assertBoolean"], 
            [CONST_ASSERTION_DISABLED],
            [
                BinaryExpr(BinaryExpr(CONST_ASSERTION_DISABLED, BinaryOp.NE, CONST_ZERO, 0), BinaryOp.EQ, CONST_ZERO, 1),
                BinaryExpr("jpamb/cases/Simple:assertBoolean:input:a:1", BinaryOp.NE, CONST_ZERO, 2)
            ],
            3
        ),
    33 : ExpectedResult(
            ["jpamb/cases/Simple:assertFalse"], 
            [CONST_ASSERTION_DISABLED], 
            [BinaryExpr(BinaryExpr(CONST_ASSERTION_DISABLED, BinaryOp.NE, CONST_ZERO, 0), BinaryOp.EQ, CONST_ZERO, 1)], 
            2
        ),
    34 : ExpectedResult(
            ["jpamb/cases/Simple:assertInteger"], 
            [CONST_ASSERTION_DISABLED],
            [
                BinaryExpr(BinaryExpr(CONST_ASSERTION_DISABLED, BinaryOp.NE, CONST_ZERO, 0), BinaryOp.EQ, CONST_ZERO, 1),
                BinaryExpr(BinaryExpr("jpamb/cases/Simple:assertInteger:input:a:0", BinaryOp.NE, CONST_ZERO, 2), BinaryOp.EQ, CONST_ZERO, 3)
            ],
            4
        ),
    35 : ExpectedResult(
            ["jpamb/cases/Simple:assertInteger"], 
            [CONST_ASSERTION_DISABLED],
            [
                BinaryExpr(BinaryExpr(CONST_ASSERTION_DISABLED, BinaryOp.NE, CONST_ZERO, 0), BinaryOp.EQ, CONST_ZERO, 1),
                BinaryExpr("jpamb/cases/Simple:assertInteger:input:a:1", BinaryOp.NE, CONST_ZERO, 2)
            ],
            3
        ),
    36 : ExpectedResult(
            ["jpamb/cases/Simple:assertPositive"], 
            [CONST_ASSERTION_DISABLED],
            [
                BinaryExpr(BinaryExpr(CONST_ASSERTION_DISABLED, BinaryOp.NE, CONST_ZERO, 0), BinaryOp.EQ, CONST_ZERO, 1),
                BinaryExpr(BinaryExpr("jpamb/cases/Simple:assertPositive:input:a:-1", BinaryOp.GT, CONST_ZERO, 2), BinaryOp.EQ, CONST_ZERO, 3)
            ],
            4
        ),
    37 : ExpectedResult(
            ["jpamb/cases/Simple:assertPositive"], 
            [CONST_ASSERTION_DISABLED], 
            [
                BinaryExpr(BinaryExpr(CONST_ASSERTION_DISABLED, BinaryOp.NE, CONST_ZERO, 0), BinaryOp.EQ, CONST_ZERO, 1),
                BinaryExpr("jpamb/cases/Simple:assertPositive:input:a:1", BinaryOp.GT, CONST_ZERO, 2)
            ],
            3
        ),
    38 : ExpectedResult(
            ["jpamb/cases/Simple:checkBeforeAssert"], 
            [
                CONST_ASSERTION_DISABLED,
                "jpamb/cases/Simple:checkBeforeAssert:5"
            ], 
            [
                BinaryExpr("jpamb/cases/Simple:checkBeforeAssert:input:a:-1", BinaryOp.NE, CONST_ZERO, 0),
                BinaryExpr(BinaryExpr(CONST_ASSERTION_DISABLED, BinaryOp.NE, CONST_ZERO, 1), BinaryOp.EQ, CONST_ZERO, 2),
                BinaryExpr("jpamb/cases/Simple:checkBeforeAssert:input:a:-1", BinaryOp.NE, 0, 3),
                BinaryExpr(BinaryExpr(BinaryExpr("jpamb/cases/Simple:checkBeforeAssert:5", BinaryOp.DIV, "jpamb/cases/Simple:checkBeforeAssert:input:a:-1", 4), BinaryOp.GT, CONST_ZERO, 5), BinaryOp.EQ, CONST_ZERO, 6)
            ], 
            7
        ),
    39 : ExpectedResult(
            ["jpamb/cases/Simple:checkBeforeAssert"], 
            [],
            [BinaryExpr(BinaryExpr("jpamb/cases/Simple:checkBeforeAssert:input:a:0", BinaryOp.NE, CONST_ZERO, 0), BinaryOp.EQ, CONST_ZERO, 1)], 
            2
        ),
    40 : ExpectedResult(
            ["jpamb/cases/Simple:checkBeforeDivideByN2"], 
            [
                CONST_ASSERTION_DISABLED,
                "jpamb/cases/Simple:checkBeforeDivideByN2:8",
                "jpamb/cases/Simple:checkBeforeDivideByN2:15"
            ],
            [
                BinaryExpr("jpamb/cases/Simple:checkBeforeDivideByN2:input:a:0", BinaryOp.EQ, CONST_ZERO, 0),
                BinaryExpr(BinaryExpr(CONST_ASSERTION_DISABLED, BinaryOp.NE, CONST_ZERO, 1), BinaryOp.EQ, CONST_ZERO, 2),
                BinaryExpr("jpamb/cases/Simple:checkBeforeDivideByN2:8", BinaryOp.GT, "jpamb/cases/Simple:checkBeforeDivideByN2:input:a:0", 3)
            ],
            4
        ),
    41 : ExpectedResult(
            ["jpamb/cases/Simple:checkBeforeDivideByN2"], 
            ["jpamb/cases/Simple:checkBeforeDivideByN2:2"],
            [
                BinaryExpr(BinaryExpr("jpamb/cases/Simple:checkBeforeDivideByN2:input:a:1", BinaryOp.EQ, CONST_ZERO, 0), BinaryOp.EQ, CONST_ZERO, 1),
                BinaryExpr("jpamb/cases/Simple:checkBeforeDivideByN2:input:a:1", BinaryOp.NE, 0, 2),
            ],
            3
        ),
    42 : ExpectedResult(
            ["jpamb/cases/Simple:checkBeforeDivideByN"],  
            [CONST_ASSERTION_DISABLED], 
            [
                BinaryExpr(BinaryExpr(CONST_ASSERTION_DISABLED, BinaryOp.NE, CONST_ZERO, 0), BinaryOp.EQ, CONST_ZERO, 1),
                BinaryExpr(BinaryExpr("jpamb/cases/Simple:checkBeforeDivideByN:input:a:0", BinaryOp.NE, CONST_ZERO, 2), BinaryOp.EQ, CONST_ZERO, 3)
            ],
            4
        ),
    43 : ExpectedResult(
            ["jpamb/cases/Simple:checkBeforeDivideByN"], 
            [
                CONST_ASSERTION_DISABLED,
                "jpamb/cases/Simple:checkBeforeDivideByN:8"
            ],
            [
                BinaryExpr(BinaryExpr(CONST_ASSERTION_DISABLED, BinaryOp.NE, CONST_ZERO, 0), BinaryOp.EQ, CONST_ZERO, 1),
                BinaryExpr("jpamb/cases/Simple:checkBeforeDivideByN:input:a:1", BinaryOp.NE, CONST_ZERO, 2),
                BinaryExpr("jpamb/cases/Simple:checkBeforeDivideByN:input:a:1", BinaryOp.NE, CONST_ZERO, 3)
            ],
            4
        ),
    44 : ExpectedResult(
            ["jpamb/cases/Simple:divideByN"], 
            ["jpamb/cases/Simple:divideByN:0"], 
            [BinaryExpr("jpamb/cases/Simple:divideByN:input:a:0", BinaryOp.EQ, CONST_ZERO, 0)], 
            1
        ),
    45 : ExpectedResult(
            ["jpamb/cases/Simple:divideByN"], 
            ["jpamb/cases/Simple:divideByN:0"], 
            [BinaryExpr("jpamb/cases/Simple:divideByN:input:a:1", BinaryOp.NE, 0, 0)],
            1
        ),
    46 : ExpectedResult(
            ["jpamb/cases/Simple:divideByNMinus10054203"], 
            [
                "jpamb/cases/Simple:divideByNMinus10054203:0",
                "jpamb/cases/Simple:divideByNMinus10054203:2"
            ], 
            [BinaryExpr(BinaryExpr("jpamb/cases/Simple:divideByNMinus10054203:input:a:0", BinaryOp.SUB, "jpamb/cases/Simple:divideByNMinus10054203:2", 0), BinaryOp.NE, CONST_ZERO, 1)], 
            2
        ),
    47 : ExpectedResult(
            ["jpamb/cases/Simple:divideByNMinus10054203"], 
            [
                "jpamb/cases/Simple:divideByNMinus10054203:0",
                "jpamb/cases/Simple:divideByNMinus10054203:2"
            ],
            [BinaryExpr(BinaryExpr("jpamb/cases/Simple:divideByNMinus10054203:input:a:10054203", BinaryOp.SUB, "jpamb/cases/Simple:divideByNMinus10054203:2", 0), BinaryOp.EQ, CONST_ZERO, 1)],
            2
        ),
    48 : ExpectedResult(
            ["jpamb/cases/Simple:divideByZero"], 
            [
                "jpamb/cases/Simple:divideByZero:0",
                "jpamb/cases/Simple:divideByZero:1"
            ], 
            [BinaryExpr("jpamb/cases/Simple:divideByZero:1", BinaryOp.EQ, CONST_ZERO, 0)], 
            1
        ),
    49 : ExpectedResult(
            ["jpamb/cases/Simple:divideZeroByZero"], 
            [], 
            [BinaryExpr("jpamb/cases/Simple:divideZeroByZero:input:b:0", BinaryOp.EQ, CONST_ZERO, 0)], 
            1
        ),
    50 : ExpectedResult(
            ["jpamb/cases/Simple:divideZeroByZero"], 
            [], 
            [BinaryExpr("jpamb/cases/Simple:divideZeroByZero:input:b:1", BinaryOp.NE, CONST_ZERO, 0)], 
            1
        ),
    51 : ExpectedResult(
            ["jpamb/cases/Simple:earlyReturn"], 
            ["jpamb/cases/Simple:earlyReturn:0"], 
            [], 
            0
        ),
    52 : ExpectedResult(
            ["jpamb/cases/Simple:justReturn"], 
            ["jpamb/cases/Simple:justReturn:0"], 
            [], 
            0
        ),
    53 : ExpectedResult(
            ["jpamb/cases/Simple:justReturnNothing"], 
            [], 
            [], 
            0
        ),
    54 : ExpectedResult(
            ["jpamb/cases/Simple:multiError"], 
            [CONST_ASSERTION_DISABLED], 
            [
                BinaryExpr(BinaryExpr(CONST_ASSERTION_DISABLED, BinaryOp.NE, CONST_ZERO, 0), BinaryOp.EQ, CONST_ZERO, 1),
                BinaryExpr(BinaryExpr("jpamb/cases/Simple:multiError:input:a:0", BinaryOp.NE, CONST_ZERO, 2), BinaryOp.EQ, CONST_ZERO, 3)
            ], 
            4
        ),
    55 : ExpectedResult(
            ["jpamb/cases/Simple:multiError"], 
            [
                CONST_ASSERTION_DISABLED,
                "jpamb/cases/Simple:multiError:8",
                "jpamb/cases/Simple:multiError:9"
            ],
            [
                BinaryExpr(BinaryExpr(CONST_ASSERTION_DISABLED, BinaryOp.NE, CONST_ZERO, 0), BinaryOp.EQ, CONST_ZERO, 1),
                BinaryExpr("jpamb/cases/Simple:multiError:input:a:1", BinaryOp.NE, CONST_ZERO, 2),
                BinaryExpr("jpamb/cases/Simple:multiError:9", BinaryOp.EQ, CONST_ZERO, 3)
            ],
            4
        ),
    56 : ExpectedResult(
            ["jpamb/cases/Tricky:collatz"], 
            [CONST_ASSERTION_DISABLED], 
            [ 
                BinaryExpr(BinaryExpr(CONST_ASSERTION_DISABLED, BinaryOp.NE, CONST_ZERO, 0), BinaryOp.EQ, CONST_ZERO, 1),
                BinaryExpr(BinaryExpr("jpamb/cases/Tricky:collatz:input:a:0", BinaryOp.GT, CONST_ZERO, 2), BinaryOp.EQ, CONST_ZERO, 3)
            ], 
            4
        ),
    57 : ExpectedResult(
            ["jpamb/cases/Tricky:collatz"], 
            [], 
            [], 
            0
        )
}
