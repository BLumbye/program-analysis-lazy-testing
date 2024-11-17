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

# TODO: taken from jpamb/bin/test.py
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
JPAMB_EXPECTED_RESULTS = {
    0 : ExpectedResult(
            ["jpamb/cases/Arrays:arrayContent"], 
            [
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
                BinaryExpr(BinaryExpr("jpamb/cases/Arrays:arrayContent:23", BinaryOp.GE, "jpamb/cases/Arrays:arrayContent:0", 0), BinaryOp.EQ, CONST_ZERO, 1),
                BinaryExpr(BinaryExpr(CONST_ASSERTION_DISABLED, BinaryOp.NE, CONST_ZERO, 2), BinaryOp.EQ, CONST_ZERO, 3),
                BinaryExpr(BinaryExpr("jpamb/cases/Arrays:arrayContent:23", BinaryOp.GT, CONST_ZERO, 4), BinaryOp.EQ, CONST_ZERO, 5)
            ], 
            6
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
            [],
            0
        ),
    2 : ExpectedResult(
            ["jpamb/cases/Arrays:arrayIsNull"], 
            [
                "jpamb/cases/Arrays:arrayIsNull:0",
                "jpamb/cases/Arrays:arrayIsNull:3",
                "jpamb/cases/Arrays:arrayIsNull:4"
            ], 
            [], 
            0
        ),
    3 : ExpectedResult( #TODO: handle null values in diff!
            ["jpamb/cases/Arrays:arrayIsNullLength"], 
            [
                "jpamb/cases/Arrays:arrayIsNullLength:0"
            ], 
            [
               BinaryExpr(BinaryExpr(CONST_ASSERTION_DISABLED, BinaryOp.NE, CONST_ZERO, 0), BinaryOp.EQ, CONST_ZERO, 1)
            ], 
            2
        ),
    4 : ExpectedResult(
            ["jpamb/cases/Arrays:arrayLength"], 
            [
                "jpamb/cases/Arrays:arrayLength:0",
                "jpamb/cases/Arrays:arrayLength:3",
                "jpamb/cases/Arrays:arrayLength:4",
                "jpamb/cases/Arrays:arrayLength:7",
                "jpamb/cases/Arrays:arrayLength:8",
                "jpamb/cases/Arrays:arrayLength:15"
            ], 
            [
                BinaryExpr(BinaryExpr(CONST_ASSERTION_DISABLED, BinaryOp.NE, CONST_ZERO, 0), BinaryOp.EQ, CONST_ZERO, 1),
                BinaryExpr("jpamb/cases/Arrays:arrayLength:0", BinaryOp.EQ, "jpamb/cases/Arrays:arrayLength:15", 2)
            ], 
            3
        ),
    5 : ExpectedResult( #TODO: better array input handling
            ["jpamb/cases/Arrays:arrayNotEmpty"], 
            [], 
            [
                BinaryExpr(BinaryExpr(CONST_ASSERTION_DISABLED, BinaryOp.NE, CONST_ZERO, 0), BinaryOp.EQ, CONST_ZERO, 1),
                BinaryExpr("jpamb/cases/Arrays:arrayNotEmpty:input:a:1", BinaryOp.GT, CONST_ZERO, 2)
            ], 
            3
        ),
    6 : ExpectedResult(
            ["jpamb/cases/Arrays:arrayNotEmpty"], 
            [], 
            [
                BinaryExpr(BinaryExpr(CONST_ASSERTION_DISABLED, BinaryOp.NE, CONST_ZERO, 0), BinaryOp.EQ, CONST_ZERO, 1),
                BinaryExpr(BinaryExpr("jpamb/cases/Arrays:arrayNotEmpty:input:a:0", BinaryOp.GT, CONST_ZERO, 2), BinaryOp.EQ, CONST_ZERO, 3)
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
            [], 
            0
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
            [BinaryExpr(BinaryExpr("jpamb/cases/Arrays:arraySometimesNull:input:a:0", BinaryOp.GE, "jpamb/cases/Arrays:arraySometimesNull:3", 0), BinaryOp.EQ, CONST_ZERO, 1)], 
            2
        ),
    9 : ExpectedResult(
            ["jpamb/cases/Arrays:arraySometimesNull"], 
            [
                "jpamb/cases/Arrays:arraySometimesNull:0",
                "jpamb/cases/Arrays:arraySometimesNull:3",
                "jpamb/cases/Arrays:arraySometimesNull:13",
                "jpamb/cases/Arrays:arraySometimesNull:14"
            ], 
            [BinaryExpr("jpamb/cases/Arrays:arraySometimesNull:input:a:11", BinaryOp.GE, "jpamb/cases/Arrays:arraySometimesNull:3", 0)], 
            1
        ),
    10 : ExpectedResult(
            ["jpamb/cases/Arrays:arraySpellsHello"], 
            [
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
                BinaryExpr(BinaryExpr("jpamb/cases/Arrays:arraySpellsHello:input:a:104", BinaryOp.NE, "jpamb/cases/Arrays:arraySpellsHello:5", 2), BinaryOp.EQ, CONST_ZERO, 3),
                BinaryExpr(BinaryExpr("jpamb/cases/Arrays:arraySpellsHello:input:a:101", BinaryOp.NE, "jpamb/cases/Arrays:arraySpellsHello:10", 4), BinaryOp.EQ, CONST_ZERO, 5),
                BinaryExpr(BinaryExpr("jpamb/cases/Arrays:arraySpellsHello:input:a:108", BinaryOp.NE, "jpamb/cases/Arrays:arraySpellsHello:15", 6), BinaryOp.EQ, CONST_ZERO, 7),
                BinaryExpr(BinaryExpr("jpamb/cases/Arrays:arraySpellsHello:input:a:108", BinaryOp.NE, "jpamb/cases/Arrays:arraySpellsHello:20", 8), BinaryOp.EQ, CONST_ZERO, 9),
                BinaryExpr("jpamb/cases/Arrays:arraySpellsHello:input:a:111", BinaryOp.EQ, "jpamb/cases/Arrays:arraySpellsHello:25", 10)
            ], 
            11
        ),
    11 : ExpectedResult(
            ["jpamb/cases/Arrays:arraySpellsHello"], 
            [
                "jpamb/cases/Arrays:arraySpellsHello:3",
                "jpamb/cases/Arrays:arraySpellsHello:5"
            ], 
            [
                BinaryExpr(BinaryExpr(CONST_ASSERTION_DISABLED, BinaryOp.NE, CONST_ZERO, 0), BinaryOp.EQ, CONST_ZERO, 1),
                BinaryExpr("jpamb/cases/Arrays:arraySpellsHello:input:a:120", BinaryOp.NE, "jpamb/cases/Arrays:arraySpellsHello:5", 2),
            ],
            3
        ),
    12 : ExpectedResult(
            ["jpamb/cases/Arrays:arraySpellsHello"], 
            [
                "jpamb/cases/Arrays:arraySpellsHello:3"
            ], 
            [
                BinaryExpr(BinaryExpr(CONST_ASSERTION_DISABLED, BinaryOp.NE, CONST_ZERO, 0), BinaryOp.EQ, CONST_ZERO, 1)
            ],
            2
        ),
    13 : ExpectedResult(
            ["jpamb/cases/Arrays:arraySumIsLarge"], 
            [
                "jpamb/cases/Arrays:arraySumIsLarge:0",  # sum
                "jpamb/cases/Arrays:arraySumIsLarge:2",  # i
                "jpamb/cases/Arrays:arraySumIsLarge:14", # ++
                "jpamb/cases/Arrays:arraySumIsLarge:19"  # 300
            ], 
            [
                BinaryExpr(BinaryExpr("jpamb/cases/Arrays:arraySumIsLarge:2", BinaryOp.GE, "jpamb/cases/Arrays:arraySumIsLarge:input:a:3", 0), BinaryOp.EQ, CONST_ZERO, 1),
                BinaryExpr(BinaryExpr(BinaryExpr("jpamb/cases/Arrays:arraySumIsLarge:2", BinaryOp.ADD, "jpamb/cases/Arrays:arraySumIsLarge:14", 3), BinaryOp.GE, "jpamb/cases/Arrays:arraySumIsLarge:input:a:3", 4), BinaryOp.EQ, CONST_ZERO, 5),
                BinaryExpr(BinaryExpr(BinaryExpr(BinaryExpr("jpamb/cases/Arrays:arraySumIsLarge:2", BinaryOp.ADD, "jpamb/cases/Arrays:arraySumIsLarge:14", 3), BinaryOp.ADD, "jpamb/cases/Arrays:arraySumIsLarge:14", 7), BinaryOp.GE, "jpamb/cases/Arrays:arraySumIsLarge:input:a:3", 8), BinaryOp.EQ, CONST_ZERO, 9),
                BinaryExpr(BinaryExpr(BinaryExpr(BinaryExpr("jpamb/cases/Arrays:arraySumIsLarge:2", BinaryOp.ADD, "jpamb/cases/Arrays:arraySumIsLarge:14", 3), BinaryOp.ADD, "jpamb/cases/Arrays:arraySumIsLarge:14", 7), BinaryOp.ADD, "jpamb/cases/Arrays:arraySumIsLarge:14", 11), BinaryOp.GE, "jpamb/cases/Arrays:arraySumIsLarge:input:a:3", 12),
                BinaryExpr(BinaryExpr(CONST_ASSERTION_DISABLED, BinaryOp.NE, CONST_ZERO, 13), BinaryOp.EQ, CONST_ZERO, 14),
                BinaryExpr(BinaryExpr(BinaryExpr(BinaryExpr("jpamb/cases/Arrays:arraySumIsLarge:0", BinaryOp.ADD, "jpamb/cases/Arrays:arraySumIsLarge:input:a:50", 2), BinaryOp.ADD, "jpamb/cases/Arrays:arraySumIsLarge:input:a:100", 6), BinaryOp.ADD, "jpamb/cases/Arrays:arraySumIsLarge:input:a:200", 10), BinaryOp.GT, "jpamb/cases/Arrays:arraySumIsLarge:19", 15)
            ], 
            16
        ),
    14 : ExpectedResult(
            ["jpamb/cases/Arrays:arraySumIsLarge"], 
            [
                "jpamb/cases/Arrays:arraySumIsLarge:0", # sum
                "jpamb/cases/Arrays:arraySumIsLarge:2", # i
                "jpamb/cases/Arrays:arraySumIsLarge:19" # 300
            ],
            [
                BinaryExpr("jpamb/cases/Arrays:arraySumIsLarge:2", BinaryOp.GE, "jpamb/cases/Arrays:arraySumIsLarge:input:a:0", 0),
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
            [], 
            [BinaryExpr(BinaryExpr(CONST_ASSERTION_DISABLED, BinaryOp.NE, CONST_ZERO, 0), BinaryOp.EQ, CONST_ZERO, 1)], 
            2
        ),
    21 : ExpectedResult(
            [
                "jpamb/cases/Calls:callsAssertFib", 
                "jpamb/cases/Calls:fib"
            ], 
            ["jpamb/cases/Calls:callsAssertFib:4"], 
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
            [], 
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
            [
                BinaryExpr("jpamb/cases/Loops:neverAsserts:0", BinaryOp.LE, CONST_ZERO, 0)
                #  until limit
            ], 
            1
        ),
    29 : ExpectedResult(
            ["jpamb/cases/Loops:neverDivides"], 
            ["jpamb/cases/Loops:neverDivides:0"], 
            [
                BinaryExpr("jpamb/cases/Loops:neverDivides:0", BinaryOp.LE, CONST_ZERO, 0)
                #  until limit
            ], 
            1
        ),
    # TODO: fix cache_ids
    # TODO: can we avoid repeating expressions
    30 : ExpectedResult(
            ["jpamb/cases/Loops:terminates"], 
            [
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
            [],
            [
                BinaryExpr(BinaryExpr(CONST_ASSERTION_DISABLED, BinaryOp.NE, CONST_ZERO, 0), BinaryOp.EQ, CONST_ZERO, 1),
                BinaryExpr(BinaryExpr("jpamb/cases/Simple:assertBoolean:input:a:0", BinaryOp.NE, CONST_ZERO, 2), BinaryOp.EQ, CONST_ZERO, 3)
            ],
            4
        ),
    32 : ExpectedResult(
            ["jpamb/cases/Simple:assertBoolean"], 
            [],
            [
                BinaryExpr(BinaryExpr(CONST_ASSERTION_DISABLED, BinaryOp.NE, CONST_ZERO, 0), BinaryOp.EQ, CONST_ZERO, 1),
                BinaryExpr("jpamb/cases/Simple:assertBoolean:input:a:1", BinaryOp.NE, CONST_ZERO, 2)
            ],
            3
        ),
    33 : ExpectedResult(
            ["jpamb/cases/Simple:assertFalse"], 
            [], 
            [BinaryExpr(BinaryExpr(CONST_ASSERTION_DISABLED, BinaryOp.NE, CONST_ZERO, 0), BinaryOp.EQ, CONST_ZERO, 1)], 
            2
        ),
    34 : ExpectedResult(
            ["jpamb/cases/Simple:assertInteger"], 
            [],
            [
                BinaryExpr(BinaryExpr(CONST_ASSERTION_DISABLED, BinaryOp.NE, CONST_ZERO, 0), BinaryOp.EQ, CONST_ZERO, 1),
                BinaryExpr(BinaryExpr("jpamb/cases/Simple:assertInteger:input:a:0", BinaryOp.NE, CONST_ZERO, 2), BinaryOp.EQ, CONST_ZERO, 3)
            ],
            4
        ),
    35 : ExpectedResult(
            ["jpamb/cases/Simple:assertInteger"], 
            [],
            [
                BinaryExpr(BinaryExpr(CONST_ASSERTION_DISABLED, BinaryOp.NE, CONST_ZERO, 0), BinaryOp.EQ, CONST_ZERO, 1),
                BinaryExpr("jpamb/cases/Simple:assertInteger:input:a:1", BinaryOp.NE, CONST_ZERO, 2)
            ],
            3
        ),
    36 : ExpectedResult(
            ["jpamb/cases/Simple:assertPositive"], 
            [],
            [
                BinaryExpr(BinaryExpr(CONST_ASSERTION_DISABLED, BinaryOp.NE, CONST_ZERO, 0), BinaryOp.EQ, CONST_ZERO, 1),
                BinaryExpr(BinaryExpr("jpamb/cases/Simple:assertPositive:input:a:-1", BinaryOp.GT, CONST_ZERO, 2), BinaryOp.EQ, CONST_ZERO, 3)
            ],
            4
        ),
    37 : ExpectedResult(
            ["jpamb/cases/Simple:assertPositive"], 
            [], 
            [
                BinaryExpr(BinaryExpr(CONST_ASSERTION_DISABLED, BinaryOp.NE, CONST_ZERO, 0), BinaryOp.EQ, CONST_ZERO, 1),
                BinaryExpr("jpamb/cases/Simple:assertPositive:input:a:1", BinaryOp.GT, CONST_ZERO, 2)
            ],
            3
        ),
    38 : ExpectedResult(
            ["jpamb/cases/Simple:checkBeforeAssert"], 
            ["jpamb/cases/Simple:checkBeforeAssert:5"], 
            [
                BinaryExpr("jpamb/cases/Simple:checkBeforeAssert:input:a:-1", BinaryOp.NE, CONST_ZERO, 0),
                BinaryExpr(BinaryExpr(CONST_ASSERTION_DISABLED, BinaryOp.NE, CONST_ZERO, 1), BinaryOp.EQ, CONST_ZERO, 2),
                BinaryExpr(BinaryExpr(BinaryExpr("jpamb/cases/Simple:checkBeforeAssert:5", BinaryOp.DIV, "jpamb/cases/Simple:checkBeforeAssert:input:a:-1", 3), BinaryOp.GT, CONST_ZERO, 4), BinaryOp.EQ, CONST_ZERO, 5)
            ], 
            6
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
            [BinaryExpr(BinaryExpr("jpamb/cases/Simple:checkBeforeDivideByN2:input:a:1", BinaryOp.EQ, CONST_ZERO, 0), BinaryOp.EQ, CONST_ZERO, 1)],
            2
        ),
    42 : ExpectedResult(
            ["jpamb/cases/Simple:checkBeforeDivideByN"],  
            [], 
            [
                BinaryExpr(BinaryExpr(CONST_ASSERTION_DISABLED, BinaryOp.NE, CONST_ZERO, 0), BinaryOp.EQ, CONST_ZERO, 1),
                BinaryExpr(BinaryExpr("jpamb/cases/Simple:checkBeforeDivideByN:input:a:0", BinaryOp.NE, CONST_ZERO, 2), BinaryOp.EQ, CONST_ZERO, 3)
            ],
            4
        ),
    43 : ExpectedResult(
            ["jpamb/cases/Simple:checkBeforeDivideByN"], 
            ["jpamb/cases/Simple:checkBeforeDivideByN:8"], 
            [
                BinaryExpr(BinaryExpr(CONST_ASSERTION_DISABLED, BinaryOp.NE, CONST_ZERO, 0), BinaryOp.EQ, CONST_ZERO, 1),
                BinaryExpr("jpamb/cases/Simple:checkBeforeDivideByN:input:a:1", BinaryOp.NE, CONST_ZERO, 2)
            ],
            3
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
            [], 
            0
        ),
    46 : ExpectedResult(
            ["jpamb/cases/Simple:divideByNMinus10054203"], 
            [
                "jpamb/cases/Simple:divideByNMinus10054203:0",
                "jpamb/cases/Simple:divideByNMinus10054203:2"
            ], 
            [], 
            0
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
            [], 
            0
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
            [], 
            [
                BinaryExpr(BinaryExpr(CONST_ASSERTION_DISABLED, BinaryOp.NE, CONST_ZERO, 0), BinaryOp.EQ, CONST_ZERO, 1),
                BinaryExpr(BinaryExpr("jpamb/cases/Simple:multiError:input:a:0", BinaryOp.NE, CONST_ZERO, 2), BinaryOp.EQ, CONST_ZERO, 3)
            ], 
            4
        ),
    55 : ExpectedResult(
            ["jpamb/cases/Simple:multiError"], 
            [
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
            [], 
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
