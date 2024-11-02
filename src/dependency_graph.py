from interpreter import SimpleInterpreter, Method
from dataclasses import dataclass
from collections import deque
import jpamb_utils as utils
import json

from utils.method_loader import JavaClass, load_class


def create_dependency_graph(java_class: JavaClass, method_name: str) -> list[str]:
    interpreter = SimpleInterpreter(
        java_class=java_class,
        method_stack=deque(
            [Method(java_class.methods[method_name].bytecode, [], [], 0)])
    )

    # Step through the program and build the dependency graph
    # TODO: Handle other invokations than static
    # TODO: Handle failing tests
    limit = 1000
    dependencies = []
    while interpreter.step_count < limit and interpreter.done is None:
        next = interpreter.method_stack[-1].bytecode[interpreter.method_stack[-1].pc]
        if next["opr"] == "invoke" and next["access"] == "static":
            method_name = next["method"]["name"]
            dependencies.append(method_name)
        interpreter.step()
    return dependencies


def run_tests(java_class: JavaClass, old_dependencies: dict[str, list[str]] = {}):
    dependency_graph: dict[str, list[str]] = old_dependencies.copy()
    tests = filter(lambda method: method.is_test, java_class.methods.values())
    for test in tests:
        dependencies = create_dependency_graph(java_class, test.name)
        dependency_graph[test.name] = dependencies
    json_dependency_graph = json.dumps(dependency_graph)
    return json_dependency_graph


if __name__ == "__main__":
    java_class = load_class(
        "codebases/constant_becomes_equal/next/decompiled/Simple.json")
    print(run_tests(java_class, {}))
