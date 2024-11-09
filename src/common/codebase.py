import os
import json
from dataclasses import dataclass
from common.common import abs_method_name, all_file_paths

# Can both be a next and previous codebase
@dataclass
class Codebase:
    # classname -> list of bytecode for fields
    _fields: dict[str, list[object]]
    # classname -> methodname -> list of methods (they might have different arguments)
    _methods: dict[str, dict[str, list[object]]]
    # classname -> list of bytecode for test methods
    _tests: dict[str, list[object]]
    # classname -> bytecode for class
    bytecode = dict[str, object]

    def __init__(self, bytecode: dict[str, object]):
        self.bytecode = bytecode
        self._fields = {}
        self._methods = {}
        self._tests = {}

        for class_name, _class in bytecode.items():
            self._methods.setdefault(class_name, {})
            self._tests.setdefault(class_name, [])
            self._fields[class_name] = _class["fields"]

            for method in _class["methods"]:
                method_name = method["name"]
                is_test = any(a["type"] == "utils/Test" for a in method["annotations"])
                if is_test:
                    self._tests[class_name].append(method)

                self._methods[class_name].setdefault(method_name, []).append(method)            

    def get_classes(self) -> dict[str, object]:
        return self.bytecode
    
    def get_class_names(self) -> list[str]:
        return self.bytecode.keys()

    def get_class(self, class_name) -> object:
        return self.bytecode[class_name]

    def get_class_methods(self, class_name) -> dict[str, list[object]]:
        return self._methods[class_name]

    def get_method(self, class_name, method_name, arguments) -> object:
        # TODO: handle argument overloading
        return self._methods[class_name][method_name][0]
    
    def get_tests(self) -> dict[str, object]:
        return self._tests
    
    def get_class_tests(self, class_name) -> list[object]:
        return self._tests[class_name]

    def get_fields(self) -> dict[str, list[object]]:
        return self._fields
    
    def all_test_names(self) -> list[str]:
        test_names = []
        for c, tests in self.get_tests().items():
            for t in tests:
                test_names.append(abs_method_name(c, t["name"]))
        return test_names
    
def code_base_path(codebase: str):
    return os.path.join(os.path.dirname(__file__), "..", "..", "codebases", codebase)

def load_decompiled(codebase_dir: str, is_next: bool) -> Codebase:
    bytecode = dict()
    dir = "next" if is_next else "previous"
    for name, file_path in all_file_paths(os.path.join(codebase_dir, dir, "decompiled")):
        with open(file_path, 'r') as file:
            bytecode[name] = json.load(file)

    return Codebase(bytecode)

def load_codebase(codebase: str, is_next: bool) -> Codebase:
    return load_decompiled(code_base_path(codebase), is_next)
