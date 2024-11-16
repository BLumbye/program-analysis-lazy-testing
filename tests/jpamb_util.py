import os
import json
import re
from typing import Generator
from dataclasses import dataclass
from jpamb_utils import *
from src.common.common import all_file_paths
from src.common.codebase import Codebase
from src.common.binary_expression import BinaryExpr

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
    amount_of_constants: list[str]
    constraints: list[BinaryExpr]
    cache_size: int

# Based on jpamb/stats/cases.txt
# TODO: missing values
JPAMB_EXPECTED_RESULTS = {
    0 : ExpectedResult(
            ["jpamb/cases/Arrays:arrayContent"], 
            [], 
            [], 
            0
        ),
    1 : ExpectedResult(
            ["jpamb/cases/Arrays:arrayInBounds"], 
            [], 
            [], 
            0
        ),
    2 : ExpectedResult(
            ["jpamb/cases/Arrays:arrayIsNull"], 
            [], 
            [], 
            0
        ),
    3 : ExpectedResult(
            ["jpamb/cases/Arrays:arrayIsNullLength"], 
            [], 
            [], 
            0
        ),
    4 : ExpectedResult(
            ["jpamb/cases/Arrays:arrayLength"], 
            [], 
            [], 
            0
        ),
    5 : ExpectedResult(
            ["jpamb/cases/Arrays:arrayNotEmpty"], 
            [], 
            [], 
            0
        ),
    6 : ExpectedResult(
            ["jpamb/cases/Arrays:arrayNotEmpty"], 
            [], 
            [], 
            0
        ),
    7 : ExpectedResult(
            ["jpamb/cases/Arrays:arrayOutOfBounds"], 
            [], 
            [], 
            0
        ),
    8 : ExpectedResult(
            ["jpamb/cases/Arrays:arraySometimesNull"], 
            [], 
            [], 
            0
        ),
    9 : ExpectedResult(
            ["jpamb/cases/Arrays:arraySometimesNull"], 
            [], 
            [], 
            0
        ),
    10 : ExpectedResult(
            ["jpamb/cases/Arrays:arraySpellsHello"], 
            [], 
            [], 
            0
        ),
    11 : ExpectedResult(
            ["jpamb/cases/Arrays:arraySpellsHello"], 
            [], 
            [], 
            0
        ),
    12 : ExpectedResult(
            ["jpamb/cases/Arrays:arraySpellsHello"], 
            [], 
            [], 
            0
        ),
    13 : ExpectedResult(
            ["jpamb/cases/Arrays:arraySumIsLarge"], 
            [], 
            [], 
            0
        ),
    14 : ExpectedResult(
            ["jpamb/cases/Arrays:arraySumIsLarge"], 
            [], 
            [], 
            0
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
            ["jpamb/cases/Calls:allPrimesArePositive", "jpamb/cases/Calls:generatePrimeArray"], 
            [], 
            [], 
            0
        ),
    18 : ExpectedResult(
            ["jpamb/cases/Calls:allPrimesArePositive", "jpamb/cases/Calls:generatePrimeArray"], 
            [], 
            [], 
            0
        ),
    19 : ExpectedResult(
            ["jpamb/cases/Calls:allPrimesArePositive", "jpamb/cases/Calls:generatePrimeArray"], 
            [], 
            [], 
            0
        ),
    20 : ExpectedResult(
            ["jpamb/cases/Calls:callsAssertFalse", "jpamb/cases/Calls:assertFalse"], 
            [], 
            [], 
            0
        ),
    21 : ExpectedResult(
            ["jpamb/cases/Calls:callsAssertFib", "jpamb/cases/Calls:fib"], 
            [], 
            [], 
            0
        ),
    22 : ExpectedResult(
            ["jpamb/cases/Calls:callsAssertFib", "jpamb/cases/Calls:fib"], 
            [], 
            [], 
            0
        ),
    23 : ExpectedResult(
            ["jpamb/cases/Calls:callsAssertIf", "jpamb/cases/Calls:assertIf", "jpamb/cases/Calls:assertFalse"], 
            [], 
            [], 
            0
        ),
    24 : ExpectedResult(
            ["jpamb/cases/Calls:callsAssertIf", "jpamb/cases/Calls:assertIf", "jpamb/cases/Calls:assertTrue"], 
            [], 
            [], 
            0
        ),
    25 : ExpectedResult(
            ["jpamb/cases/Calls:callsAssertIfWithTrue", "jpamb/cases/Calls:assertIf", "jpamb/cases/Calls:assertTrue"], 
            [], 
            [], 
            0
        ),
    26 : ExpectedResult(
            ["jpamb/cases/Calls:callsAssertTrue", "jpamb/cases/Calls:assertTrue"], 
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
            [], 
            [], 
            0
        ),
    29 : ExpectedResult(
            ["jpamb/cases/Loops:neverDivides"], 
            [], 
            [], 
            0
        ),
    30 : ExpectedResult(
            ["jpamb/cases/Loops:terminates"], 
            [], 
            [], 
            0
        ),
    31 : ExpectedResult(
            ["jpamb/cases/Simple:assertBoolean"], 
            [], 
            [], 
            0
        ),
    32 : ExpectedResult(
            ["jpamb/cases/Simple:assertBoolean"], 
            [], 
            [], 
            0
        ),
    33 : ExpectedResult(
            ["jpamb/cases/Simple:assertFalse"], 
            [], 
            [], 
            0
        ),
    34 : ExpectedResult(
            ["jpamb/cases/Simple:assertInteger"], 
            [], 
            [], 
            0
        ),
    35 : ExpectedResult(
            ["jpamb/cases/Simple:assertInteger"], 
            [], 
            [], 
            0
        ),
    36 : ExpectedResult(
            ["jpamb/cases/Simple:assertPositive"], 
            [], 
            [], 
            0
        ),
    37 : ExpectedResult(
            ["jpamb/cases/Simple:assertPositive"], 
            [], 
            [], 
            0
        ),
    38 : ExpectedResult(
            ["jpamb/cases/Simple:checkBeforeAssert"], 
            [], 
            [], 
            0
        ),
    39 : ExpectedResult(
            ["jpamb/cases/Simple:checkBeforeAssert"], 
            [], 
            [], 
            0
        ),
    40 : ExpectedResult(
            ["jpamb/cases/Simple:checkBeforeDivideByN2"], 
            [], 
            [], 
            0
        ),
    41 : ExpectedResult(
            ["jpamb/cases/Simple:checkBeforeDivideByN2"], 
            [], 
            [], 
            0
        ),
    42 : ExpectedResult(
            ["jpamb/cases/Simple:checkBeforeDivideByN"], 
            [], 
            [], 
            0
        ),
    43 : ExpectedResult(
            ["jpamb/cases/Simple:checkBeforeDivideByN"], 
            [], 
            [], 
            0
        ),
    44 : ExpectedResult(
            ["jpamb/cases/Simple:divideByN"], 
            [], 
            [], 
            0
        ),
    45 : ExpectedResult(
            ["jpamb/cases/Simple:divideByN"], 
            [], 
            [], 
            0
        ),
    46 : ExpectedResult(
            ["jpamb/cases/Simple:divideByNMinus10054203"], 
            [], 
            [], 
            0
        ),
    47 : ExpectedResult(
            ["jpamb/cases/Simple:divideByNMinus10054203"], 
            [], 
            [], 
            0
        ),
    48 : ExpectedResult(
            ["jpamb/cases/Simple:divideByZero"], 
            [], 
            [], 
            0
        ),
    49 : ExpectedResult(
            ["jpamb/cases/Simple:divideZeroByZero"], 
            [], 
            [], 
            0
        ),
    50 : ExpectedResult(
            ["jpamb/cases/Simple:divideZeroByZero"], 
            [], 
            [], 
            0
        ),
    51 : ExpectedResult(
            ["jpamb/cases/Simple:earlyReturn"], 
            [], 
            [], 
            0
        ),
    52 : ExpectedResult(
            ["jpamb/cases/Simple:justReturn"], 
            [], 
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
            [], 
            0
        ),
    55 : ExpectedResult(
            ["jpamb/cases/Simple:multiError"], 
            [], 
            [], 
            0
        ),
    56 : ExpectedResult(
            ["jpamb/cases/Tricky:collatz"], 
            [], 
            [], 
            0
        ),
    57 : ExpectedResult(
            ["jpamb/cases/Tricky:collatz"], 
            [], 
            [], 
            0
        )
}
