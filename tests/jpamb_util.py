import os
import json
import re
from typing import Generator
from dataclasses import dataclass
from jpamb_utils import *
from src.common.common import all_file_paths
from src.common.codebase import Codebase

def load_jpamb_suite() -> Codebase:
    bytecode = dict()
    json_path = os.path.join(os.path.dirname(__file__), "jpamb", "decompiled")
    for name, file_path in all_file_paths(json_path):
        with open(file_path, 'r') as file:
            bytecode[name] = json.load(file)

    return Codebase(bytecode)

@dataclass(frozen=True)
class Case:
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
def parse_case(line) -> Case:
    if not (m := re.match(r"([^ ]*) +(\([^)]*\)) -> (.*)", line)):
        raise ValueError(f"Unexpected line: {line!r}")
    
    method_id = MethodId.parse(m.group(1))
    inputs = list(map(convert_jpamb_input, InputParser.parse(m.group(2))))

    return Case(method_id.class_name.replace(".", "/"), method_id.method_name, inputs, m.group(3))

def prepare_cases() -> Generator[Case, None, None]:
    cases_path = os.path.join(os.path.dirname(__file__), "jpamb", "stats", "cases.txt")
    with open(cases_path, 'r') as file:
        for ls in file.readlines():
            yield parse_case(ls[:-1])
